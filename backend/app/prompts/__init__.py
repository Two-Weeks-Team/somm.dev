"""Sommelier evaluation prompts package.

This package contains the prompt templates for each sommelier agent,
each designed with unique personality and evaluation focus areas.
"""

from app.prompts.marcel import get_marcel_prompt
from app.prompts.isabella import get_isabella_prompt
from app.prompts.heinrich import get_heinrich_prompt
from app.prompts.sofia import get_sofia_prompt
from app.prompts.laurent import get_laurent_prompt
from app.prompts.jeanpierre import get_jeanpierre_prompt

__all__ = [
    "get_marcel_prompt",
    "get_isabella_prompt",
    "get_heinrich_prompt",
    "get_sofia_prompt",
    "get_laurent_prompt",
    "get_jeanpierre_prompt",
]
