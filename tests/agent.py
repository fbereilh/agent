"""Tests for agent module."""

import os
import pytest
from agent import RestaurantAgent, get_system_prompt


def test_get_system_prompt():
    """Test system prompt generation."""
    prompt = get_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "La Roca Village" in prompt
    assert "restaurante" in prompt.lower()


def test_agent_initialization():
    """Test agent can be initialized."""
    agent = RestaurantAgent(db_path="test_chromadb")
    assert agent.chat is not None
    assert agent.search is not None
    assert len(agent.history) > 0  # Should have welcome message


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="API key not available")
def test_agent_chat():
    """Test agent can respond to messages."""
    agent = RestaurantAgent(db_path="test_chromadb")
    response = agent("Hola")
    assert response is not None
    assert len(agent.history) > 1  # Welcome + user message + response
