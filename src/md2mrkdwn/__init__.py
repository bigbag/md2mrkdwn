"""md2mrkdwn - Convert Markdown to Slack mrkdwn format."""

from md2mrkdwn.converter import (
    DEFAULT_CONFIG,
    MrkdwnConfig,
    MrkdwnConverter,
    convert,
)

__version__ = "0.2.0"
__all__ = [
    "MrkdwnConverter",
    "MrkdwnConfig",
    "DEFAULT_CONFIG",
    "convert",
    "__version__",
]
