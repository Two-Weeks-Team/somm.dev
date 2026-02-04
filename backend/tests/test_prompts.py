"""Comprehensive tests for all sommelier prompt templates."""

import pytest


class TestMarcelPrompt:
    """Tests for Marcel's prompt template."""

    def test_marcel_prompt_has_system_and_human_messages(self):
        """Test that Marcel's prompt has both system and human messages."""
        from app.prompts.marcel import get_marcel_prompt

        prompt = get_marcel_prompt()
        messages = list(prompt.messages)
        assert len(messages) == 2
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_marcel_prompt_contains_focus_areas(self):
        """Test that Marcel's prompt contains key focus areas."""
        from app.prompts.marcel import get_marcel_prompt

        prompt = get_marcel_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert "structure" in system_message.lower()
        assert "organization" in system_message.lower()
        assert "metrics" in system_message.lower()

    def test_marcel_prompt_uses_wine_metaphors(self):
        """Test that Marcel's prompt uses wine metaphors."""
        from app.prompts.marcel import get_marcel_prompt

        prompt = get_marcel_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "cellar" in system_message.lower()
            or "wine" in system_message.lower()
            or "vintage" in system_message.lower()
        )


class TestIsabellaPrompt:
    """Tests for Isabella's prompt template."""

    def test_isabella_prompt_has_system_and_human_messages(self):
        """Test that Isabella's prompt has both system and human messages."""
        from app.prompts.isabella import get_isabella_prompt

        prompt = get_isabella_prompt()
        messages = list(prompt.messages)
        assert len(messages) == 2
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_isabella_prompt_contains_focus_areas(self):
        """Test that Isabella's prompt contains key focus areas."""
        from app.prompts.isabella import get_isabella_prompt

        prompt = get_isabella_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert "aesthetic" in system_message.lower()
        assert "readability" in system_message.lower()

    def test_isabella_prompt_uses_wine_metaphors(self):
        """Test that Isabella's prompt uses poetic wine metaphors."""
        from app.prompts.isabella import get_isabella_prompt

        prompt = get_isabella_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "wine" in system_message.lower()
            or "vintage" in system_message.lower()
            or "bouquet" in system_message.lower()
        )


class TestHeinrichPrompt:
    """Tests for Heinrich's prompt template."""

    def test_heinrich_prompt_has_system_and_human_messages(self):
        """Test that Heinrich's prompt has both system and human messages."""
        from app.prompts.heinrich import get_heinrich_prompt

        prompt = get_heinrich_prompt()
        messages = list(prompt.messages)
        assert len(messages) == 2
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_heinrich_prompt_contains_focus_areas(self):
        """Test that Heinrich's prompt contains key focus areas."""
        from app.prompts.heinrich import get_heinrich_prompt

        prompt = get_heinrich_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "test" in system_message.lower()
            or "security" in system_message.lower()
            or "quality" in system_message.lower()
        )

    def test_heinrich_prompt_emphasizes_rigor(self):
        """Test that Heinrich's prompt emphasizes rigor and methodology."""
        from app.prompts.heinrich import get_heinrich_prompt

        prompt = get_heinrich_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "rigor" in system_message.lower()
            or "methodical" in system_message.lower()
            or "thorough" in system_message.lower()
        )


class TestSofiaPrompt:
    """Tests for Sofia's prompt template."""

    def test_sofia_prompt_has_system_and_human_messages(self):
        """Test that Sofia's prompt has both system and human messages."""
        from app.prompts.sofia import get_sofia_prompt

        prompt = get_sofia_prompt()
        messages = list(prompt.messages)
        assert len(messages) == 2
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_sofia_prompt_contains_focus_areas(self):
        """Test that Sofia's prompt contains key focus areas."""
        from app.prompts.sofia import get_sofia_prompt

        prompt = get_sofia_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "innovation" in system_message.lower() or "modern" in system_message.lower()
        )

    def test_sofia_prompt_is_forward_looking(self):
        """Test that Sofia's prompt is forward-looking and curious."""
        from app.prompts.sofia import get_sofia_prompt

        prompt = get_sofia_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "future" in system_message.lower()
            or "growth" in system_message.lower()
            or "curious" in system_message.lower()
        )


class TestLaurentPrompt:
    """Tests for Laurent's prompt template."""

    def test_laurent_prompt_has_system_and_human_messages(self):
        """Test that Laurent's prompt has both system and human messages."""
        from app.prompts.laurent import get_laurent_prompt

        prompt = get_laurent_prompt()
        messages = list(prompt.messages)
        assert len(messages) == 2
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_laurent_prompt_contains_focus_areas(self):
        """Test that Laurent's prompt contains key focus areas."""
        from app.prompts.laurent import get_laurent_prompt

        prompt = get_laurent_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "implementation" in system_message.lower()
            or "algorithm" in system_message.lower()
            or "craft" in system_message.lower()
        )

    def test_laurent_prompt_is_pragmatic(self):
        """Test that Laurent's prompt is pragmatic and detail-oriented."""
        from app.prompts.laurent import get_laurent_prompt

        prompt = get_laurent_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "pragmatic" in system_message.lower()
            or "detail" in system_message.lower()
            or "craft" in system_message.lower()
        )


class TestJeanPierrePrompt:
    """Tests for Jean-Pierre's prompt template."""

    def test_jeanpierre_prompt_has_system_and_human_messages(self):
        """Test that Jean-Pierre's prompt has both system and human messages."""
        from app.prompts.jeanpierre import get_jeanpierre_prompt

        prompt = get_jeanpierre_prompt()
        messages = list(prompt.messages)
        assert len(messages) == 2
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_jeanpierre_prompt_includes_all_sommeliers(self):
        """Test that Jean-Pierre's prompt includes all other sommeliers."""
        from app.prompts.jeanpierre import get_jeanpierre_prompt

        prompt = get_jeanpierre_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert "Marcel" in system_message
        assert "Isabella" in system_message
        assert "Heinrich" in system_message
        assert "Sofia" in system_message
        assert "Laurent" in system_message

    def test_jeanpierre_prompt_focuses_on_synthesis(self):
        """Test that Jean-Pierre's prompt focuses on final synthesis."""
        from app.prompts.jeanpierre import get_jeanpierre_prompt

        prompt = get_jeanpierre_prompt()
        messages = list(prompt.messages)
        system_message = messages[0].prompt.template
        assert (
            "synthes" in system_message.lower()
            or "final" in system_message.lower()
            or "verdict" in system_message.lower()
        )

    def test_jeanpierre_prompt_has_synthesis_variables(self):
        """Test that Jean-Pierre's human prompt has synthesis variables."""
        from app.prompts.jeanpierre import get_jeanpierre_prompt

        prompt = get_jeanpierre_prompt()
        messages = list(prompt.messages)
        human_message = messages[1].prompt.template
        assert "marcel_result" in human_message
        assert "isabella_result" in human_message
        assert "heinrich_result" in human_message
        assert "sofia_result" in human_message
        assert "laurent_result" in human_message


class TestPromptsPackage:
    """Tests for the prompts package __init__."""

    def test_prompts_package_exports_all_prompts(self):
        """Test that prompts package exports all prompt functions."""
        from app import prompts

        assert hasattr(prompts, "get_marcel_prompt")
        assert hasattr(prompts, "get_isabella_prompt")
        assert hasattr(prompts, "get_heinrich_prompt")
        assert hasattr(prompts, "get_sofia_prompt")
        assert hasattr(prompts, "get_laurent_prompt")
        assert hasattr(prompts, "get_jeanpierre_prompt")

    def test_all_prompts_return_chat_prompt_template(self):
        """Test that all prompt functions return ChatPromptTemplate."""
        from langchain_core.prompts import ChatPromptTemplate
        from app.prompts import (
            get_marcel_prompt,
            get_isabella_prompt,
            get_heinrich_prompt,
            get_sofia_prompt,
            get_laurent_prompt,
            get_jeanpierre_prompt,
        )

        prompts_list = [
            get_marcel_prompt,
            get_isabella_prompt,
            get_heinrich_prompt,
            get_sofia_prompt,
            get_laurent_prompt,
            get_jeanpierre_prompt,
        ]

        for get_prompt in prompts_list:
            prompt = get_prompt()
            assert isinstance(prompt, ChatPromptTemplate)
