"""Markdown to Slack mrkdwn converter."""

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from md2mrkdwn.patterns import (
    BOLD_ASTERISKS_PATTERN,
    BOLD_ITALIC_ASTERISKS_PATTERN,
    BOLD_ITALIC_UNDERSCORES_PATTERN,
    BOLD_PLACEHOLDER,
    BOLD_STRIP_PATTERN,
    BOLD_UNDERSCORES_PATTERN,
    BULLET,
    CHECKBOX_CHECKED,
    CHECKBOX_UNCHECKED,
    EMOJI_SHORTCODE_PATTERN,
    HEADER_PATTERN,
    HORIZONTAL_LINE,
    HORIZONTAL_RULE_PATTERN,
    IMAGE_PATTERN,
    INLINE_CODE_PATTERN,
    ITALIC_ASTERISKS_PATTERN,
    ITALIC_PLACEHOLDER,
    ITALIC_STRIP_PATTERN,
    ITALIC_UNDERSCORES_PATTERN,
    LINK_PATTERN,
    SEPARATOR_CELL_PATTERN,
    STRIKETHROUGH_PATTERN,
    TABLE_ROW_PATTERN,
    TASK_CHECKED_PATTERN,
    TASK_UNCHECKED_PATTERN,
    UNORDERED_LIST_PATTERN,
)


class HeaderStyle(str, Enum):
    BOLD = "bold"
    PLAIN = "plain"
    PREFIX = "prefix"


class LinkFormat(str, Enum):
    SLACK = "slack"
    URL_ONLY = "url_only"
    TEXT_ONLY = "text_only"


class TableMode(str, Enum):
    CODE_BLOCK = "code_block"
    PRESERVE = "preserve"


@dataclass(frozen=True, slots=True)
class MrkdwnConfig:
    """Configuration for Markdown to mrkdwn conversion."""

    # Character/Symbol configuration
    bullet_char: str = BULLET
    checkbox_checked: str = CHECKBOX_CHECKED
    checkbox_unchecked: str = CHECKBOX_UNCHECKED
    horizontal_rule_char: str = HORIZONTAL_LINE
    horizontal_rule_length: int = 10

    # Mode settings
    header_style: HeaderStyle = HeaderStyle.BOLD
    link_format: LinkFormat = LinkFormat.SLACK
    table_mode: TableMode = TableMode.CODE_BLOCK
    table_link_format: LinkFormat = LinkFormat.URL_ONLY
    strip_table_emoji: bool = True
    convert_table_links: bool = True

    # Element enable/disable flags
    convert_bold: bool = True
    convert_italic: bool = True
    convert_strikethrough: bool = True
    convert_links: bool = True
    convert_images: bool = True
    convert_lists: bool = True
    convert_task_lists: bool = True
    convert_headers: bool = True
    convert_horizontal_rules: bool = True
    convert_tables: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""

        if self.horizontal_rule_length < 1:
            raise ValueError("horizontal_rule_length must be at least 1")


DEFAULT_CONFIG = MrkdwnConfig()


class MrkdwnConverter:
    """Convert Markdown to Slack mrkdwn format.

    This converter transforms standard CommonMark Markdown into Slack's
    proprietary mrkdwn format, handling the differences in syntax for
    bold, italic, links, and other formatting elements.
    """

    def __init__(self, config: MrkdwnConfig | None = None) -> None:
        """Initialize the converter.

        Args:
            config: Optional configuration. Uses default if not provided.
        """
        self._config = config or DEFAULT_CONFIG
        self._in_code_block = False
        self._table_placeholders: dict[str, str] = {}

    def convert(self, markdown: str) -> str:
        """Convert Markdown text to Slack mrkdwn format.

        Args:
            markdown: Input text in Markdown format

        Returns:
            Text converted to Slack mrkdwn format
        """
        if not markdown:
            return markdown

        self._in_code_block = False
        self._table_placeholders = {}

        text = markdown.strip()

        # Step 1: Extract and placeholder tables (before any conversion)
        text = self._process_tables(text)

        # Step 2: Process line by line, skipping code blocks
        lines = text.splitlines()
        result_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                self._in_code_block = not self._in_code_block
                result_lines.append(line)
                continue

            if self._in_code_block:
                result_lines.append(line)
                continue

            converted_line = self._apply_patterns(line)
            result_lines.append(converted_line)

        text = "\n".join(result_lines)

        # Step 3: Restore tables
        for placeholder, table in self._table_placeholders.items():
            text = text.replace(placeholder, table)

        return text

    def _apply_patterns(self, line: str) -> str:
        """Apply all conversion patterns to a line.

        Uses placeholders to prevent pattern interference (e.g., bold converted
        result being matched by italic pattern).

        Args:
            line: Single line of text

        Returns:
            Converted line
        """
        config = self._config

        # Check if line contains inline code - we need to protect it
        code_segments: dict[str, str] = {}
        if "`" in line:
            line, code_segments = self._protect_inline_code(line)

        # Step 1: Convert bold+italic first (uses both asterisks and underscores)
        if config.convert_bold or config.convert_italic:
            # Compute wrapper based on which conversions are enabled
            if config.convert_bold and config.convert_italic:
                open_wrap = f"{BOLD_PLACEHOLDER}{ITALIC_PLACEHOLDER}"
                close_wrap = f"{ITALIC_PLACEHOLDER}{BOLD_PLACEHOLDER}"
            elif config.convert_bold:
                open_wrap = close_wrap = BOLD_PLACEHOLDER
            else:  # only italic
                open_wrap = close_wrap = ITALIC_PLACEHOLDER

            def wrap_bold_italic(m: re.Match[str]) -> str:
                return f"{open_wrap}{m.group(1)}{close_wrap}"

            line = BOLD_ITALIC_ASTERISKS_PATTERN.sub(wrap_bold_italic, line)
            line = BOLD_ITALIC_UNDERSCORES_PATTERN.sub(wrap_bold_italic, line)

        # Step 2: Convert bold (before italic to prevent interference)
        if config.convert_bold:
            line = BOLD_ASTERISKS_PATTERN.sub(
                lambda m: f"{BOLD_PLACEHOLDER}{m.group(1)}{BOLD_PLACEHOLDER}",
                line,
            )
            line = BOLD_UNDERSCORES_PATTERN.sub(
                lambda m: f"{BOLD_PLACEHOLDER}{m.group(1)}{BOLD_PLACEHOLDER}",
                line,
            )

        # Step 3: Convert italic
        if config.convert_italic:
            line = ITALIC_ASTERISKS_PATTERN.sub(
                lambda m: f"{ITALIC_PLACEHOLDER}{m.group(1)}{ITALIC_PLACEHOLDER}",
                line,
            )
            line = ITALIC_UNDERSCORES_PATTERN.sub(
                lambda m: f"{ITALIC_PLACEHOLDER}{m.group(1)}{ITALIC_PLACEHOLDER}",
                line,
            )

        # Step 4: Convert other patterns
        if config.convert_strikethrough:
            line = STRIKETHROUGH_PATTERN.sub(r"~\1~", line)

        # Handle images - must come before links to prevent link pattern matching
        image_segments: dict[str, str] = {}
        if config.convert_images:
            line = IMAGE_PATTERN.sub(r"<\2>", line)
        elif config.convert_links:
            # Protect images from link pattern when images disabled but links enabled
            replacer = self._create_placeholder_replacer(image_segments, "IMG")
            line = IMAGE_PATTERN.sub(replacer, line)

        if config.convert_links:
            if config.link_format == LinkFormat.SLACK:
                line = LINK_PATTERN.sub(r"<\2|\1>", line)
            elif config.link_format == LinkFormat.URL_ONLY:
                line = LINK_PATTERN.sub(r"<\2>", line)
            elif config.link_format == LinkFormat.TEXT_ONLY:
                line = LINK_PATTERN.sub(r"\1", line)

        if config.convert_task_lists:
            line = TASK_CHECKED_PATTERN.sub(f"\\1{config.bullet_char} {config.checkbox_checked} ", line)
            line = TASK_UNCHECKED_PATTERN.sub(f"\\1{config.bullet_char} {config.checkbox_unchecked} ", line)
        elif config.convert_lists:
            # Task lists disabled but lists enabled - convert to regular bullets
            line = TASK_CHECKED_PATTERN.sub(f"\\1{config.bullet_char} ", line)
            line = TASK_UNCHECKED_PATTERN.sub(f"\\1{config.bullet_char} ", line)

        if config.convert_lists:
            line = UNORDERED_LIST_PATTERN.sub(f"\\1{config.bullet_char} ", line)

        if config.convert_horizontal_rules:
            hr = config.horizontal_rule_char * config.horizontal_rule_length
            line = HORIZONTAL_RULE_PATTERN.sub(hr, line)

        if config.convert_headers:
            if config.header_style == HeaderStyle.BOLD:

                def convert_header(m: re.Match[str]) -> str:
                    content = m.group(1)
                    # Strip any existing bold/italic placeholders to avoid doubling
                    content = content.replace(BOLD_PLACEHOLDER, "")
                    content = content.replace(ITALIC_PLACEHOLDER, "")
                    return f"{BOLD_PLACEHOLDER}{content}{BOLD_PLACEHOLDER}"

                line = HEADER_PATTERN.sub(convert_header, line)
            elif config.header_style == HeaderStyle.PLAIN:

                def strip_header(m: re.Match[str]) -> str:
                    content = m.group(1)
                    # Strip any existing bold/italic placeholders
                    content = content.replace(BOLD_PLACEHOLDER, "")
                    content = content.replace(ITALIC_PLACEHOLDER, "")
                    return content

                line = HEADER_PATTERN.sub(strip_header, line)
            # HeaderStyle.PREFIX - leave unchanged

        # Step 5: Replace placeholders with final mrkdwn characters
        line = line.replace(BOLD_PLACEHOLDER, "*")
        line = line.replace(ITALIC_PLACEHOLDER, "_")

        # Step 6: Restore inline code segments
        for placeholder, code in code_segments.items():
            line = line.replace(placeholder, code)

        # Step 7: Restore protected images (when images disabled but links enabled)
        for placeholder, image in image_segments.items():
            line = line.replace(placeholder, image)

        return line

    @staticmethod
    def _create_placeholder_replacer(segments: dict[str, str], prefix: str) -> Callable[[re.Match[str]], str]:
        """Create a replacer function for placeholder protection.

        Args:
            segments: Dict to store placeholder -> original content mapping
            prefix: Prefix for placeholder names (e.g., "CODE", "IMG")

        Returns:
            Replacer function for use with re.sub
        """
        counter = [0]  # Use list for mutable counter in closure

        def replacer(match: re.Match[str]) -> str:
            placeholder = f"%%{prefix}_{counter[0]}%%"
            segments[placeholder] = match.group(0)
            counter[0] += 1
            return placeholder

        return replacer

    def _protect_inline_code(self, line: str) -> tuple[str, dict[str, str]]:
        """Protect inline code segments with placeholders.

        Args:
            line: Line containing inline code

        Returns:
            Tuple of (protected line, mapping of placeholder to code)
        """
        code_segments: dict[str, str] = {}
        replacer = self._create_placeholder_replacer(code_segments, "CODE")
        protected_line = INLINE_CODE_PATTERN.sub(replacer, line)
        return protected_line, code_segments

    def _process_tables(self, text: str) -> str:
        """Find and wrap markdown tables in code blocks.

        Slack doesn't support markdown tables natively, so we wrap them
        in code blocks to preserve formatting with monospace display.

        Args:
            text: Full text content

        Returns:
            Text with tables wrapped in code blocks via placeholders
        """
        if not self._config.convert_tables or self._config.table_mode == TableMode.PRESERVE:
            return text

        lines = text.split("\n")
        result_lines: list[str] = []
        i = 0
        in_code_block = False

        while i < len(lines):
            line = lines[i]

            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                result_lines.append(line)
                i += 1
                continue

            if in_code_block:
                result_lines.append(line)
                i += 1
                continue

            if not self._is_table_line(line):
                result_lines.append(line)
                i += 1
                continue

            table_lines = self._collect_table_lines(lines, i)
            if len(table_lines) >= 2 and self._is_valid_table(table_lines):
                wrapped = self._wrap_table(table_lines)
                placeholder = self._generate_placeholder(wrapped)
                self._table_placeholders[placeholder] = wrapped
                result_lines.append(placeholder)
                i += len(table_lines)
                continue

            result_lines.append(line)
            i += 1

        return "\n".join(result_lines)

    @staticmethod
    def _is_table_line(line: str) -> bool:
        """Check if a line could be part of a markdown table.

        Args:
            line: Line to check

        Returns:
            True if line matches table row pattern
        """
        return TABLE_ROW_PATTERN.match(line) is not None

    def _collect_table_lines(self, lines: list[str], start_idx: int) -> list[str]:
        """Collect consecutive table-like lines starting from an index.

        Args:
            lines: All lines
            start_idx: Index to start collecting from

        Returns:
            List of consecutive table-like lines
        """
        table_lines = [lines[start_idx]]
        j = start_idx + 1
        while j < len(lines) and self._is_table_line(lines[j]):
            table_lines.append(lines[j])
            j += 1
        return table_lines

    def _is_valid_table(self, table_lines: list[str]) -> bool:
        """Check if lines form a valid markdown table.

        A valid table has:
        - A header row
        - A separator row (dashes with optional alignment colons)
        - Matching column counts

        Args:
            table_lines: Lines to validate

        Returns:
            True if valid markdown table
        """
        if len(table_lines) < 2:
            return False

        header_cells = self._parse_row(table_lines[0])
        separator_cells = self._parse_row(table_lines[1])

        if len(header_cells) != len(separator_cells):
            return False

        return self._is_separator_row(separator_cells)

    def _parse_row(self, row: str) -> list[str]:
        """Parse a markdown table row into cells.

        Args:
            row: Table row string

        Returns:
            List of cell contents
        """
        stripped = row.strip()
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        return [cell.strip() for cell in stripped.split("|")]

    def _is_separator_row(self, cells: list[str]) -> bool:
        """Check if cells form a separator row.

        Args:
            cells: Parsed cells from a row

        Returns:
            True if all cells match separator pattern
        """
        return bool(cells) and all(SEPARATOR_CELL_PATTERN.match(cell) for cell in cells)

    def _display_width(self, text: str) -> int:
        """Calculate display width accounting for wide Unicode characters.

        Standard emoji and many Unicode symbols render as 2 columns wide in
        monospace fonts, but Python's len() returns 1. This method provides
        accurate display width for table column alignment.

        Args:
            text: Text to measure

        Returns:
            Display width in monospace columns
        """
        width = 0
        for char in text:
            # Simplified heuristic: characters above U+1F00 are treated as double-width.
            # This covers most emoji (U+1F300+) but is imprecise for some ranges
            # (e.g., CJK below U+1F00 would need wcwidth for accuracy).
            # Acceptable trade-off for a zero-dependency library.
            if ord(char) > 0x1F00:
                width += 2
            else:
                width += 1
        return width

    def _ljust_display(self, text: str, width: int) -> str:
        """Left-justify string based on display width, not character count.

        Args:
            text: Text to pad
            width: Target display width

        Returns:
            Text padded with spaces to reach target width
        """
        current_width = self._display_width(text)
        padding = width - current_width
        if padding > 0:
            return text + " " * padding
        return text

    def _wrap_table(self, table_lines: list[str]) -> str:
        """Wrap table lines in a code block."""
        clean_lines = []
        for line in table_lines:
            line = self._strip_markdown(line)
            if self._config.convert_table_links:
                line = self._convert_table_links(line)
            line = self._process_emoji(line)
            clean_lines.append(line)

        # Realign columns after all transformations
        clean_lines = self._align_table_columns(clean_lines)

        return "```\n" + "\n".join(clean_lines) + "\n```"

    def _strip_markdown(self, text: str) -> str:
        """Strip markdown bold/italic formatting from text."""
        text = BOLD_STRIP_PATTERN.sub(r"\1", text)
        text = ITALIC_STRIP_PATTERN.sub(r"\1", text)
        return text

    def _convert_table_links(self, text: str) -> str:
        """Convert markdown links in table cells based on table_link_format config."""
        fmt = self._config.table_link_format
        if fmt == LinkFormat.SLACK:
            return LINK_PATTERN.sub(r"<\2|\1>", text)
        if fmt == LinkFormat.URL_ONLY:
            return LINK_PATTERN.sub(r"\2", text)
        if fmt == LinkFormat.TEXT_ONLY:
            return LINK_PATTERN.sub(r"\1", text)
        raise ValueError(f"Unknown LinkFormat: {fmt}")

    def _process_emoji(self, text: str) -> str:
        """Strip emoji shortcodes if configured."""
        if self._config.strip_table_emoji:
            text = EMOJI_SHORTCODE_PATTERN.sub("", text)
            text = re.sub(r"  +", " ", text)  # Collapse multiple spaces
        return text

    def _align_table_columns(self, table_lines: list[str]) -> list[str]:
        """Realign table columns after content transformation."""
        if len(table_lines) < 2:
            return table_lines

        # Protect pipes inside angle brackets (slack links) before parsing
        pipe_placeholder = "\x00PIPE\x00"
        protected_lines = []
        for line in table_lines:
            protected = re.sub(r"<([^>]*)\|([^>]*)>", rf"<\1{pipe_placeholder}\2>", line)
            protected_lines.append(protected)

        parsed_rows = [self._parse_row(line) for line in protected_lines]
        col_count = len(parsed_rows[0]) if parsed_rows else 0

        # Calculate max width per column (skip separator row at index 1)
        # Use display width to account for wide Unicode characters (emoji)
        col_widths = []
        for col in range(col_count):
            widths = [self._display_width(row[col]) for i, row in enumerate(parsed_rows) if i != 1 and col < len(row)]
            col_widths.append(max(widths) if widths else 3)

        result = []
        for i, cells in enumerate(parsed_rows):
            if i == 1:  # Separator row
                row = "| " + " | ".join("-" * w for w in col_widths) + " |"
            else:
                padded = [
                    self._ljust_display(cells[j], col_widths[j]) if j < len(cells) else " " * col_widths[j]
                    for j in range(len(col_widths))
                ]
                row = "| " + " | ".join(padded) + " |"
            # Restore pipes in slack links
            row = row.replace(pipe_placeholder, "|")
            result.append(row)
        return result

    def _generate_placeholder(self, content: str) -> str:
        """Generate a unique placeholder for content.

        Args:
            content: Content to generate placeholder for

        Returns:
            Unique placeholder string
        """
        hash_val = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:8]
        return f"%%TABLE_{hash_val}%%"


def convert(markdown: str, config: MrkdwnConfig | None = None) -> str:
    """Convert Markdown text to Slack mrkdwn format.

    This is a convenience function that creates a converter instance
    and performs the conversion.

    Args:
        markdown: Input text in Markdown format
        config: Optional configuration. Uses default if not provided.

    Returns:
        Text converted to Slack mrkdwn format

    Example:
        >>> from md2mrkdwn import convert
        >>> convert("**Hello** *World*")
        '*Hello* _World_'

        >>> from md2mrkdwn import convert, MrkdwnConfig
        >>> config = MrkdwnConfig(bullet_char="-")
        >>> convert("- Item", config=config)
        '- Item'
    """
    converter = MrkdwnConverter(config)
    return converter.convert(markdown)
