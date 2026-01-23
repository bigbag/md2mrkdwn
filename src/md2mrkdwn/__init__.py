"""md2mrkdwn - Convert Markdown to Slack mrkdwn format."""

from md2mrkdwn.converter import (
    DEFAULT_CONFIG,
    HeaderStyle,
    LinkFormat,
    MrkdwnConfig,
    MrkdwnConverter,
    TableMode,
    convert,
)

__version__ = "0.4.3"
__all__ = [
    "MrkdwnConverter",
    "MrkdwnConfig",
    "DEFAULT_CONFIG",
    "HeaderStyle",
    "LinkFormat",
    "TableMode",
    "convert",
    "__version__",
]
