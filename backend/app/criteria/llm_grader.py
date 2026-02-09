"""LLM-based grader for subjective BMAD evaluation items.

This module provides the LLMGrader class for evaluating subjective BMAD items
using an LLM with structured output. It handles context assembly, prompt
formatting, response validation, and usage tracking.
"""

import asyncio
import json
from typing import Any, Optional

from app.criteria.grading_prompts import format_prompt, get_prompt


class LLMGrader:
    """Grader for subjective BMAD items using LLM-based evaluation."""

    def __init__(self):
        self.total_tokens = {"prompt_tokens": 0, "completion_tokens": 0}
        self.total_cost_usd = 0.0
        self._max_retries = 2

    async def grade_item(
        self, item_id: str, repo_context: dict, llm: Optional[Any] = None
    ) -> dict:
        """Grade a single BMAD item using LLM structured output.

        Args:
            item_id: The BMAD item ID to grade (e.g., "A1", "B2")
            repo_context: Dictionary containing repository context
            llm: Optional LLM client/instance. If None, returns placeholder.

        Returns:
            Dictionary with graded item result
        """
        prompt_config = get_prompt(item_id)
        max_score = prompt_config["max_score"]

        if llm is None:
            return {
                "item_id": item_id,
                "score": 0.0,
                "max_score": float(max_score),
                "confidence": "low",
                "evidence": ["LLM grading pending - no LLM client provided"],
                "rationale": f"Subjective evaluation for {item_id} requires LLM. Placeholder score returned.",
            }

        context = self._assemble_context(repo_context, max_chars=8000)
        prompt = format_prompt(item_id, context)

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._call_llm(llm, prompt)

                if self._validate_response(response, item_id, max_score):
                    self._update_usage(response.get("usage", {}))
                    parsed = response["parsed"]

                    return {
                        "item_id": item_id,
                        "score": float(parsed["score"]),
                        "max_score": float(max_score),
                        "confidence": parsed["confidence"],
                        "evidence": parsed["evidence"],
                        "rationale": parsed["rationale"],
                    }
                else:
                    if attempt < self._max_retries:
                        continue
                    else:
                        return {
                            "item_id": item_id,
                            "score": 0.0,
                            "max_score": float(max_score),
                            "confidence": "low",
                            "evidence": [
                                "Failed to validate LLM response after retries"
                            ],
                            "rationale": f"LLM response validation failed for {item_id}",
                        }

            except Exception as e:
                if attempt < self._max_retries:
                    continue
                else:
                    return {
                        "item_id": item_id,
                        "score": 0.0,
                        "max_score": float(max_score),
                        "confidence": "low",
                        "evidence": [f"LLM call failed: {str(e)}"],
                        "rationale": f"Error grading {item_id}: {str(e)}",
                    }

        return {
            "item_id": item_id,
            "score": 0.0,
            "max_score": float(max_score),
            "confidence": "low",
            "evidence": ["Unexpected error in grading"],
            "rationale": f"Unexpected error grading {item_id}",
        }

    async def _call_llm(self, llm: Any, prompt: str) -> dict:
        """Call the LLM with the given prompt.

        Args:
            llm: LLM client/instance
            prompt: Formatted prompt string

        Returns:
            Dictionary with parsed response and usage info
        """
        if hasattr(llm, "ainvoke"):
            response = await llm.ainvoke(prompt)
            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            usage = (
                response.usage_metadata if hasattr(response, "usage_metadata") else {}
            )
        elif hasattr(llm, "invoke"):
            # Wrap blocking call with asyncio.to_thread to avoid blocking event loop
            response = await asyncio.to_thread(llm.invoke, prompt)
            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            usage = (
                response.usage_metadata if hasattr(response, "usage_metadata") else {}
            )
        else:
            # Wrap callable with asyncio.to_thread for blocking fallback
            response = await asyncio.to_thread(llm, prompt)
            content = response if isinstance(response, str) else str(response)
            usage = {}

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                parsed = json.loads(json_str)
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(json_str)
            else:
                raise

        return {"parsed": parsed, "usage": usage}

    def _assemble_context(self, repo_context: dict, max_chars: int = 8000) -> str:
        """Assemble context from repo_context, respecting size limit.

        Args:
            repo_context: Dictionary with repository information
            max_chars: Maximum characters for the context string

        Returns:
            Assembled context string
        """
        parts = []

        readme = repo_context.get("readme", "")
        if readme:
            parts.append("=== README ===")
            parts.append(readme[:3000])
            parts.append("")

        file_tree = repo_context.get("file_tree", [])
        if file_tree:
            parts.append("=== FILE STRUCTURE ===")
            tree_str = "\n".join(file_tree[:100])
            parts.append(tree_str)
            parts.append("")

        main_files = repo_context.get("main_files", [])
        if main_files:
            parts.append("=== CODE SNIPPETS ===")
            remaining_chars = max_chars - sum(len(p) for p in parts)
            files_content = []
            current_chars = 0

            for file_info in main_files[:5]:
                path = file_info.get("path", "")
                content = file_info.get("content", "")
                if not content:
                    continue

                file_header = f"\n--- {path} ---\n"
                file_content = content[:1000]
                file_str = file_header + file_content

                if current_chars + len(file_str) > remaining_chars:
                    break

                files_content.append(file_str)
                current_chars += len(file_str)

            parts.extend(files_content)

        metadata = repo_context.get("metadata", {})
        if metadata:
            parts.append("\n=== METADATA ===")
            parts.append(json.dumps(metadata, indent=2))

        context = "\n".join(parts)
        if len(context) > max_chars:
            context = context[: max_chars - 3] + "..."

        return context

    def _validate_response(
        self, response: dict, item_id: str, max_score: float
    ) -> bool:
        """Validate LLM response for required fields and score range.

        Args:
            response: Raw response from _call_llm
            item_id: The BMAD item ID being graded
            max_score: Maximum allowed score for the item

        Returns:
            True if response is valid, False otherwise
        """
        try:
            parsed = response.get("parsed", {})

            required = ["score", "confidence", "evidence", "rationale"]
            for field in required:
                if field not in parsed:
                    return False

            score = parsed["score"]
            if not isinstance(score, (int, float)):
                return False
            if score < 0 or score > max_score:
                return False

            confidence = parsed["confidence"]
            if confidence not in ["high", "medium", "low"]:
                return False

            evidence = parsed["evidence"]
            if not isinstance(evidence, list):
                return False

            rationale = parsed["rationale"]
            if not isinstance(rationale, str):
                return False

            return True

        except Exception:
            return False

    def _update_usage(self, usage: dict) -> None:
        """Update token usage and cost tracking.

        Args:
            usage: Dictionary with usage metadata from LLM call
        """
        prompt_tokens = usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0) or usage.get(
            "completion_tokens", 0
        )

        self.total_tokens["prompt_tokens"] += prompt_tokens
        self.total_tokens["completion_tokens"] += completion_tokens

        prompt_cost = prompt_tokens * 0.00003
        completion_cost = completion_tokens * 0.00006
        self.total_cost_usd += prompt_cost + completion_cost

    def get_usage(self) -> dict:
        """Return accumulated token usage and cost.

        Returns:
            Dictionary with total tokens and estimated cost
        """
        return {
            "prompt_tokens": self.total_tokens["prompt_tokens"],
            "completion_tokens": self.total_tokens["completion_tokens"],
            "total_tokens": (
                self.total_tokens["prompt_tokens"]
                + self.total_tokens["completion_tokens"]
            ),
            "cost_usd": round(self.total_cost_usd, 6),
        }

    def reset_usage(self) -> None:
        """Reset usage tracking to zero."""
        self.total_tokens = {"prompt_tokens": 0, "completion_tokens": 0}
        self.total_cost_usd = 0.0
