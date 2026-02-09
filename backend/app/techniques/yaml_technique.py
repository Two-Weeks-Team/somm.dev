import json
import logging
import time
from typing import List

from app.criteria.bmad_items import get_item
from app.models.graph import ItemScore, TraceEvent
from app.techniques.base_technique import BaseTechnique
from app.techniques.schema import TechniqueDefinition

logger = logging.getLogger(__name__)


class YAMLTechnique(BaseTechnique):
    """Technique implementation backed by YAML definition files."""

    def __init__(self, definition: TechniqueDefinition):
        super().__init__(definition)

    def build_prompt(self, state: dict, item_id: str) -> str:
        """Assemble evaluation prompt from YAML definition + BMAD rubric + repo context."""
        parts = []

        # 1. Technique description
        parts.append(f"# Technique: {self.definition.name}")
        parts.append(f"{self.definition.description}")
        parts.append("")

        # 2. Prompt template
        parts.append("## Evaluation Instructions")
        parts.append(self.definition.prompt_template)
        parts.append("")

        # 3. BMAD item rubric
        try:
            bmad_item = get_item(item_id)
            parts.append(f"## Evaluation Item: {bmad_item.item_id} - {bmad_item.name}")
            parts.append(f"Description: {bmad_item.description}")
            parts.append(f"Maximum Score: {bmad_item.max_score}")
            parts.append("### Scoring Rubric:")
            for score_val, desc in sorted(bmad_item.rubric.items()):
                parts.append(f"  {score_val}: {desc}")
            parts.append("")
        except KeyError:
            parts.append(f"## Evaluation Item: {item_id}")
            parts.append("")

        # 4. Repository context
        repo_context = state.get("repo_context", {})
        if repo_context:
            parts.append("## Repository Context")
            if repo_context.get("repo_url"):
                parts.append(f"Repository: {repo_context['repo_url']}")
            if repo_context.get("readme"):
                parts.append(f"README:\n{repo_context['readme'][:2000]}")
            if repo_context.get("file_structure"):
                parts.append(
                    f"File Structure:\n{repo_context['file_structure'][:1000]}"
                )
            parts.append("")

        # 5. Scoring criteria from YAML
        if self.definition.scoring and self.definition.scoring.criteria:
            parts.append("## Scoring Scale")
            for score_val, desc in sorted(self.definition.scoring.criteria.items()):
                parts.append(f"  {score_val}: {desc}")
            parts.append("")

        # 6. Output format
        parts.append("## Required Output Format")
        parts.append("Respond in JSON format:")
        parts.append(
            json.dumps(
                {
                    "score": "<number within scoring range>",
                    "rationale": "<detailed explanation>",
                    "evidence": ["<specific evidence from repo>"],
                    "confidence": "<low|medium|high>",
                },
                indent=2,
            )
        )

        return "\n".join(parts)

    async def _call_llm(self, state: dict, item_id: str) -> dict:
        """Call LLM with assembled prompt. Returns raw response dict."""
        _prompt = self.build_prompt(state, item_id)

        # Get LLM provider config from state
        _api_key = self._get_api_key(state)

        # This is the integration point — actual LLM call will be implemented
        # when the LLM service layer is available. For now, raise NotImplementedError
        # to indicate subclasses or the router should provide the LLM call.
        raise NotImplementedError(
            "LLM integration not yet available. "
            "Use MockYAMLTechnique for testing or implement _call_llm in a subclass."
        )

    def _parse_response(self, response: dict, item_id: str) -> dict:
        """Parse LLM response into structured result."""
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Extract score and metadata from response
        score = float(response.get("score", 0))
        rationale = response.get("rationale", "")
        evidence = response.get("evidence", [])
        confidence = response.get("confidence", "medium")

        # Get BMAD item info for enrichment
        max_score = None
        item_name = None
        try:
            bmad = get_item(item_id)
            max_score = float(bmad.max_score)
            item_name = bmad.name
            # Clamp score to max
            score = min(score, max_score)
        except KeyError:
            pass

        item_scores = {
            item_id: ItemScore(
                item_id=item_id,
                score=score,
                evaluated_by=self.id,
                technique_id=self.id,
                timestamp=timestamp,
                item_name=item_name,
                max_score=max_score,
                status="evaluated",
                evidence=evidence if evidence else None,
                rationale=rationale if rationale else None,
                confidence=confidence,
            )
        }

        trace_events = [
            TraceEvent(
                step=0,
                timestamp=timestamp,
                agent=self.definition.category.value
                if hasattr(self.definition.category, "value")
                else str(self.definition.category),
                technique_id=self.id,
                item_id=item_id,
                action="evaluate",
                score_delta=score,
            )
        ]

        token_usage = response.get("token_usage", {})
        cost_usd = response.get("cost_usd", 0.0)

        return {
            "item_scores": item_scores,
            "trace_events": trace_events,
            "token_usage": token_usage,
            "cost_usd": cost_usd,
        }

    def evaluate_multiple_items(self, response: dict, item_ids: List[str]) -> dict:
        """Parse response for multiple BMAD items from a single technique."""
        all_scores = {}
        all_events = []
        for iid in item_ids:
            item_response = response.get(iid, response)
            parsed = self._parse_response(item_response, iid)
            all_scores.update(parsed["item_scores"])
            all_events.extend(parsed["trace_events"])
        return {"item_scores": all_scores, "trace_events": all_events}
