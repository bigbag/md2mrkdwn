"""Pytest fixtures for md2mrkdwn tests."""

import pytest

from md2mrkdwn import MrkdwnConverter


@pytest.fixture
def converter() -> MrkdwnConverter:
    """Create a fresh converter instance."""
    return MrkdwnConverter()
