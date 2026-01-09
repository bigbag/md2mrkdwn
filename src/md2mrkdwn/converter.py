"""Markdown to Slack mrkdwn converter."""

import hashlib
import re

# =============================================================================
# Compiled regex patterns (module-level for efficiency)
# =============================================================================

# Table detection
TABLE_ROW_PATTERN = re.compile(r"^\s*\|.+\|\s*$")
SEPARATOR_CELL_PATTERN = re.compile(r"^:?[-\u2013\u2014\u2212]+:?$")

# Markdown formatting (for stripping inside code blocks)
BOLD_STRIP_PATTERN = re.compile(r"\*\*(.+?)\*\*")
ITALIC_STRIP_PATTERN = re.compile(r"\*(.+?)\*")

# Inline code protection
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
TASK_UNCHECKED_PATTERN = re.compile(r"^(\s*)[-*+]\s+\[ \]\s*", re.MULTILINE)
UNORDERED_LIST_PATTERN = re.compile(r"^(\s*)[-*+]\s+", re.MULTILINE)
HORIZONTAL_RULE_PATTERN = re.compile(r"^[-*_]{3,}\s*$", re.MULTILINE)

# =============================================================================
# Constants
# =============================================================================

# Unicode characters for replacements
BULLET = "•"  # U+2022
CHECKBOX_CHECKED = "☑"  # U+2611
CHECKBOX_UNCHECKED = "☐"  # U+2610
HORIZONTAL_LINE = "─"  # U+2500

# Temporary placeholders to prevent pattern interference
_BOLD_PLACEHOLDER = "\x00BOLD\x00"
_ITALIC_PLACEHOLDER = "\x00ITALIC\x00"


# =============================================================================
# Converter class
# =============================================================================


class MrkdwnConverter:
    """Convert Markdown to Slack mrkdwn format.

    This converter transforms standard CommonMark Markdown into Slack's
    proprietary mrkdwn format, handling the differences in syntax for
    bold, italic, links, and other formatting elements.
    """

    def __init__(self) -> None:
        """Initialize the converter."""
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

        # Reset state
        self._in_code_block = False
        self._table_placeholders = {}

        text = markdown.strip()

        # Step 1: Extract and placeholder tables (before any conversion)
        text = self._process_tables(text)

        # Step 2: Process line by line, skipping code blocks
        lines = text.splitlines()
        result_lines = []

        for line in lines:
            # Check for code block markers
            stripped = line.strip()
            if stripped.startswith("```"):
                self._in_code_block = not self._in_code_block
                result_lines.append(line)
                continue

            # Skip conversion inside code blocks
            if self._in_code_block:
                result_lines.append(line)
                continue

            # Apply conversion patterns
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
        # Check if line contains inline code - we need to protect it
        code_segments: dict[str, str] = {}
        if "`" in line:
            line, code_segments = self._protect_inline_code(line)

        # Step 1: Convert bold+italic first (uses both asterisks and underscores)
        line = BOLD_ITALIC_ASTERISKS_PATTERN.sub(
            lambda m: f"{_BOLD_PLACEHOLDER}{_ITALIC_PLACEHOLDER}{m.group(1)}{_ITALIC_PLACEHOLDER}{_BOLD_PLACEHOLDER}",
            line,
        )
        line = BOLD_ITALIC_UNDERSCORES_PATTERN.sub(
            lambda m: f"{_BOLD_PLACEHOLDER}{_ITALIC_PLACEHOLDER}{m.group(1)}{_ITALIC_PLACEHOLDER}{_BOLD_PLACEHOLDER}",
            line,
        )

        # Step 2: Convert bold (before italic to prevent interference)
        line = BOLD_ASTERISKS_PATTERN.sub(
            lambda m: f"{_BOLD_PLACEHOLDER}{m.group(1)}{_BOLD_PLACEHOLDER}",
            line,
        )
        line = BOLD_UNDERSCORES_PATTERN.sub(
            lambda m: f"{_BOLD_PLACEHOLDER}{m.group(1)}{_BOLD_PLACEHOLDER}",
            line,
        )

        # Step 3: Convert italic
        line = ITALIC_ASTERISKS_PATTERN.sub(
            lambda m: f"{_ITALIC_PLACEHOLDER}{m.group(1)}{_ITALIC_PLACEHOLDER}",
            line,
        )
        line = ITALIC_UNDERSCORES_PATTERN.sub(
            lambda m: f"{_ITALIC_PLACEHOLDER}{m.group(1)}{_ITALIC_PLACEHOLDER}",
            line,
        )

        # Step 4: Convert other patterns
        line = STRIKETHROUGH_PATTERN.sub(r"~\1~", line)
        line = IMAGE_PATTERN.sub(r"<\2>", line)
        line = LINK_PATTERN.sub(r"<\2|\1>", line)
        line = TASK_CHECKED_PATTERN.sub(f"\\1{BULLET} {CHECKBOX_CHECKED} ", line)
        line = TASK_UNCHECKED_PATTERN.sub(f"\\1{BULLET} {CHECKBOX_UNCHECKED} ", line)
        line = UNORDERED_LIST_PATTERN.sub(f"\\1{BULLET} ", line)
        line = HORIZONTAL_RULE_PATTERN.sub(HORIZONTAL_LINE * 10, line)
        line = HEADER_PATTERN.sub(
            lambda m: f"{_BOLD_PLACEHOLDER}{m.group(1)}{_BOLD_PLACEHOLDER}",
            line,
        )

        # Step 5: Replace placeholders with final mrkdwn characters
        line = line.replace(_BOLD_PLACEHOLDER, "*")
        line = line.replace(_ITALIC_PLACEHOLDER, "_")

        # Step 6: Restore inline code segments
        for placeholder, code in code_segments.items():
            line = line.replace(placeholder, code)

        return line

    def _protect_inline_code(self, line: str) -> tuple[str, dict[str, str]]:
        """Protect inline code segments with placeholders.

        Args:
            line: Line containing inline code

        Returns:
            Tuple of (protected line, mapping of placeholder to code)
        """
        code_segments: dict[str, str] = {}
        counter = 0

        def save_code(match: re.Match[str]) -> str:
            nonlocal counter
            placeholder = f"%%CODE_{counter}%%"
            code_segments[placeholder] = match.group(0)
            counter += 1
            return placeholder

        protected_line = INLINE_CODE_PATTERN.sub(save_code, line)
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
        lines = text.split("\n")
        result_lines: list[str] = []
        i = 0
        in_code_block = False

        while i < len(lines):
            line = lines[i]

            # Track code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                result_lines.append(line)
                i += 1
                continue

            # Skip table detection inside code blocks
            if in_code_block:
                result_lines.append(line)
                i += 1
                continue

            # Check for potential table start
            if not TABLE_ROW_PATTERN.match(line):
                result_lines.append(line)
                i += 1
                continue

            # Collect consecutive table-like lines
            table_lines = [line]
            j = i + 1

            while j < len(lines) and TABLE_ROW_PATTERN.match(lines[j]):
                table_lines.append(lines[j])
                j += 1

            # Validate as a proper table (header + separator + data)
            if len(table_lines) >= 2 and self._is_valid_table(table_lines):
                # Create wrapped table
                wrapped = self._wrap_table(table_lines)
                # Generate unique placeholder
                placeholder = self._generate_placeholder(wrapped)
                self._table_placeholders[placeholder] = wrapped
                result_lines.append(placeholder)
                i = j
                continue

            # Not a valid table
            result_lines.append(line)
            i += 1

        return "\n".join(result_lines)

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

    def _wrap_table(self, table_lines: list[str]) -> str:
        """Wrap table lines in a code block.

        Strips markdown formatting from table content for clean display.

        Args:
            table_lines: Lines of the table

        Returns:
            Table wrapped in code block
        """
        clean_lines = [self._strip_markdown(line) for line in table_lines]
        return "```\n" + "\n".join(clean_lines) + "\n```"

    def _strip_markdown(self, text: str) -> str:
        """Strip markdown bold/italic formatting from text.

        Args:
            text: Text with potential markdown formatting

        Returns:
            Text with formatting removed
        """
        text = BOLD_STRIP_PATTERN.sub(r"\1", text)
        text = ITALIC_STRIP_PATTERN.sub(r"\1", text)
        return text

    def _generate_placeholder(self, content: str) -> str:
        """Generate a unique placeholder for content.

        Args:
            content: Content to generate placeholder for

        Returns:
            Unique placeholder string
        """
        hash_val = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:8]
        return f"%%TABLE_{hash_val}%%"


def convert(markdown: str) -> str:
    """Convert Markdown text to Slack mrkdwn format.

    This is a convenience function that creates a converter instance
    and performs the conversion.

    Args:
        markdown: Input text in Markdown format

    Returns:
        Text converted to Slack mrkdwn format

    Example:
        >>> from md2mrkdwn import convert
        >>> convert("**Hello** *World*")
        '*Hello* _World_'
    """
    converter = MrkdwnConverter()
    return converter.convert(markdown)
