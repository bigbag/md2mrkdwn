"""Regex patterns and constants for Markdown to mrkdwn conversion."""

import re

# Table patterns
TABLE_ROW_PATTERN = re.compile(r"^\s*\|.+\|\s*$")
SEPARATOR_CELL_PATTERN = re.compile(r"^:?[-\u2013\u2014\u2212]+:?$")

# Markdown stripping
BOLD_STRIP_PATTERN = re.compile(r"\*\*(.+?)\*\*")
ITALIC_STRIP_PATTERN = re.compile(r"\*(.+?)\*")

# Code protection
INLINE_CODE_PATTERN = re.compile(r"`[^`]+`")

# Conversion patterns
HEADER_PATTERN = re.compile(r"^#{1,6}\s+(.+?)(?:\s+#+)?$", re.MULTILINE)
BOLD_ITALIC_ASTERISKS_PATTERN = re.compile(r"\*\*\*(.+?)\*\*\*")
BOLD_ITALIC_UNDERSCORES_PATTERN = re.compile(r"___(.+?)___")
BOLD_ASTERISKS_PATTERN = re.compile(r"\*\*(.+?)\*\*")
BOLD_UNDERSCORES_PATTERN = re.compile(r"__(.+?)__")
ITALIC_ASTERISKS_PATTERN = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")
ITALIC_UNDERSCORES_PATTERN = re.compile(r"(?<!_)_([^_]+?)_(?!_)")
STRIKETHROUGH_PATTERN = re.compile(r"~~(.+?)~~")
IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
TASK_CHECKED_PATTERN = re.compile(r"^(\s*)[-*+]\s+\[x\]\s*", re.MULTILINE | re.IGNORECASE)
TASK_UNCHECKED_PATTERN = re.compile(r"^(\s*)[-*+]\s+\[ \]\s*", re.MULTILINE | re.IGNORECASE)
UNORDERED_LIST_PATTERN = re.compile(r"^(\s*)[-*+]\s+", re.MULTILINE)
HORIZONTAL_RULE_PATTERN = re.compile(r"^[-*_]{3,}\s*$", re.MULTILINE)
EMOJI_SHORTCODE_PATTERN = re.compile(r":([a-z0-9_+-]+):")

# Unicode constants
BULLET = "•"
CHECKBOX_CHECKED = "☑"
CHECKBOX_UNCHECKED = "☐"
HORIZONTAL_LINE = "─"

# Placeholders
BOLD_PLACEHOLDER = "\x00BOLD\x00"
ITALIC_PLACEHOLDER = "\x00ITALIC\x00"
