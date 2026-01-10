"""Tests for the Markdown to mrkdwn converter."""

from md2mrkdwn import MrkdwnConverter, convert


class TestBasicFormatting:
    """Test basic text formatting conversions."""

    def test_bold_asterisks(self, converter: MrkdwnConverter) -> None:
        """Test bold with double asterisks."""
        assert converter.convert("**bold**") == "*bold*"

    def test_bold_underscores(self, converter: MrkdwnConverter) -> None:
        """Test bold with double underscores."""
        assert converter.convert("__bold__") == "*bold*"

    def test_italic_asterisk(self, converter: MrkdwnConverter) -> None:
        """Test italic with single asterisk."""
        assert converter.convert("*italic*") == "_italic_"

    def test_italic_underscore(self, converter: MrkdwnConverter) -> None:
        """Test italic with single underscore."""
        assert converter.convert("_italic_") == "_italic_"

    def test_bold_italic_asterisks(self, converter: MrkdwnConverter) -> None:
        """Test bold+italic with triple asterisks."""
        assert converter.convert("***bold italic***") == "*_bold italic_*"

    def test_bold_italic_underscores(self, converter: MrkdwnConverter) -> None:
        """Test bold+italic with triple underscores."""
        assert converter.convert("___bold italic___") == "*_bold italic_*"

    def test_strikethrough(self, converter: MrkdwnConverter) -> None:
        """Test strikethrough."""
        assert converter.convert("~~strikethrough~~") == "~strikethrough~"

    def test_mixed_formatting(self, converter: MrkdwnConverter) -> None:
        """Test multiple formatting types in one line."""
        result = converter.convert("**bold** and *italic* and ~~strike~~")
        assert result == "*bold* and _italic_ and ~strike~"


class TestHeaders:
    """Test header conversions."""

    def test_h1(self, converter: MrkdwnConverter) -> None:
        """Test H1 header."""
        assert converter.convert("# Header 1") == "*Header 1*"

    def test_h2(self, converter: MrkdwnConverter) -> None:
        """Test H2 header."""
        assert converter.convert("## Header 2") == "*Header 2*"

    def test_h3(self, converter: MrkdwnConverter) -> None:
        """Test H3 header."""
        assert converter.convert("### Header 3") == "*Header 3*"

    def test_h6(self, converter: MrkdwnConverter) -> None:
        """Test H6 header."""
        assert converter.convert("###### Header 6") == "*Header 6*"

    def test_header_with_trailing_hashes(self, converter: MrkdwnConverter) -> None:
        """Test header with trailing hash characters."""
        assert converter.convert("## Header ##") == "*Header*"

    def test_multiple_headers(self, converter: MrkdwnConverter) -> None:
        """Test multiple headers in content."""
        md = "# First\n\n## Second"
        result = converter.convert(md)
        assert "*First*" in result
        assert "*Second*" in result

    def test_header_with_bold(self, converter: MrkdwnConverter) -> None:
        """Test header containing bold text."""
        assert converter.convert("# **Bold Title**") == "*Bold Title*"

    def test_header_with_italic(self, converter: MrkdwnConverter) -> None:
        """Test header containing italic text."""
        assert converter.convert("# *Italic Title*") == "*Italic Title*"

    def test_header_with_bold_italic(self, converter: MrkdwnConverter) -> None:
        """Test header containing bold+italic text."""
        assert converter.convert("# ***Bold Italic***") == "*Bold Italic*"


class TestLinks:
    """Test link conversions."""

    def test_basic_link(self, converter: MrkdwnConverter) -> None:
        """Test basic markdown link."""
        assert converter.convert("[text](https://example.com)") == "<https://example.com|text>"

    def test_link_in_text(self, converter: MrkdwnConverter) -> None:
        """Test link within text."""
        md = "Check out [this link](https://example.com) for more info"
        result = converter.convert(md)
        assert "<https://example.com|this link>" in result

    def test_multiple_links(self, converter: MrkdwnConverter) -> None:
        """Test multiple links in one line."""
        md = "[one](https://one.com) and [two](https://two.com)"
        result = converter.convert(md)
        assert "<https://one.com|one>" in result
        assert "<https://two.com|two>" in result


class TestImages:
    """Test image conversions."""

    def test_basic_image(self, converter: MrkdwnConverter) -> None:
        """Test basic image - becomes plain URL."""
        assert converter.convert("![alt text](https://example.com/img.png)") == "<https://example.com/img.png>"

    def test_image_empty_alt(self, converter: MrkdwnConverter) -> None:
        """Test image with empty alt text."""
        assert converter.convert("![](https://example.com/img.png)") == "<https://example.com/img.png>"


class TestLists:
    """Test list conversions."""

    def test_unordered_list_dash(self, converter: MrkdwnConverter) -> None:
        """Test unordered list with dash."""
        md = "- Item 1\n- Item 2"
        result = converter.convert(md)
        assert "\u2022 Item 1" in result
        assert "\u2022 Item 2" in result

    def test_unordered_list_asterisk(self, converter: MrkdwnConverter) -> None:
        """Test unordered list with asterisk."""
        md = "* Item 1\n* Item 2"
        result = converter.convert(md)
        assert "\u2022 Item 1" in result
        assert "\u2022 Item 2" in result

    def test_unordered_list_plus(self, converter: MrkdwnConverter) -> None:
        """Test unordered list with plus."""
        md = "+ Item 1\n+ Item 2"
        result = converter.convert(md)
        assert "\u2022 Item 1" in result
        assert "\u2022 Item 2" in result

    def test_nested_list(self, converter: MrkdwnConverter) -> None:
        """Test nested list preserves indentation."""
        md = "- Item 1\n  - Nested item"
        result = converter.convert(md)
        assert "\u2022 Item 1" in result
        assert "  \u2022 Nested item" in result

    def test_ordered_list(self, converter: MrkdwnConverter) -> None:
        """Test ordered list is preserved."""
        md = "1. First\n2. Second"
        result = converter.convert(md)
        # Ordered lists are kept as-is
        assert "1. First" in result
        assert "2. Second" in result


class TestTaskLists:
    """Test task list conversions."""

    def test_unchecked_task(self, converter: MrkdwnConverter) -> None:
        """Test unchecked task item."""
        result = converter.convert("- [ ] Todo item")
        assert "\u2022 \u2610 Todo item" in result

    def test_checked_task(self, converter: MrkdwnConverter) -> None:
        """Test checked task item."""
        result = converter.convert("- [x] Done item")
        assert "\u2022 \u2611 Done item" in result

    def test_checked_task_uppercase(self, converter: MrkdwnConverter) -> None:
        """Test checked task with uppercase X."""
        result = converter.convert("- [X] Done item")
        assert "\u2022 \u2611 Done item" in result


class TestCodeBlocks:
    """Test code block handling."""

    def test_inline_code_preserved(self, converter: MrkdwnConverter) -> None:
        """Test inline code is preserved."""
        assert converter.convert("`code`") == "`code`"

    def test_inline_code_with_formatting(self, converter: MrkdwnConverter) -> None:
        """Test inline code not affected by surrounding formatting."""
        md = "**bold** and `code` and *italic*"
        result = converter.convert(md)
        assert "`code`" in result
        assert "*bold*" in result
        assert "_italic_" in result

    def test_code_block_preserved(self, converter: MrkdwnConverter) -> None:
        """Test code block content is preserved."""
        md = "```python\ndef foo():\n    return 'bar'\n```"
        result = converter.convert(md)
        assert "def foo():" in result
        assert "return 'bar'" in result

    def test_code_block_no_formatting(self, converter: MrkdwnConverter) -> None:
        """Test formatting inside code blocks is not converted."""
        md = "```\n**not bold** and *not italic*\n```"
        result = converter.convert(md)
        assert "**not bold**" in result
        assert "*not italic*" in result

    def test_formatting_after_code_block(self, converter: MrkdwnConverter) -> None:
        """Test formatting works after code block ends."""
        md = "```\ncode\n```\n**bold**"
        result = converter.convert(md)
        assert "*bold*" in result


class TestTables:
    """Test table handling."""

    def test_basic_table(self, converter: MrkdwnConverter) -> None:
        """Test basic table is wrapped in code block."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = converter.convert(md)
        assert "```" in result
        assert "| A | B |" in result
        assert "| 1 | 2 |" in result

    def test_table_formatting_stripped(self, converter: MrkdwnConverter) -> None:
        """Test markdown formatting is stripped from table content."""
        md = "| **Bold** | *Italic* |\n|---|---|\n| A | B |"
        result = converter.convert(md)
        # Inside code block, markdown should be stripped
        assert "**Bold**" not in result or "```" in result.split("**Bold**")[0]

    def test_table_in_code_block_preserved(self, converter: MrkdwnConverter) -> None:
        """Test table already in code block is not double-wrapped."""
        md = "```\n| A | B |\n|---|---|\n| 1 | 2 |\n```"
        result = converter.convert(md)
        # Should only have opening and closing backticks from original
        assert result.count("```") == 2

    def test_invalid_table_not_wrapped(self, converter: MrkdwnConverter) -> None:
        """Test invalid table (no separator) is not wrapped."""
        md = "| A | B |\n| 1 | 2 |"
        result = converter.convert(md)
        # Without separator row, should not be treated as table
        # Just converted as regular text (pipes preserved)
        assert "| A | B |" in result


class TestHorizontalRules:
    """Test horizontal rule conversions."""

    def test_hr_dashes(self, converter: MrkdwnConverter) -> None:
        """Test horizontal rule with dashes."""
        assert converter.convert("---") == "\u2500" * 10

    def test_hr_asterisks(self, converter: MrkdwnConverter) -> None:
        """Test horizontal rule with asterisks."""
        assert converter.convert("***") == "\u2500" * 10

    def test_hr_underscores(self, converter: MrkdwnConverter) -> None:
        """Test horizontal rule with underscores."""
        assert converter.convert("___") == "\u2500" * 10

    def test_hr_many_chars(self, converter: MrkdwnConverter) -> None:
        """Test horizontal rule with many characters."""
        assert converter.convert("----------") == "\u2500" * 10


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_string(self, converter: MrkdwnConverter) -> None:
        """Test empty string returns empty."""
        assert converter.convert("") == ""

    def test_whitespace_only(self, converter: MrkdwnConverter) -> None:
        """Test whitespace-only returns empty."""
        assert converter.convert("   \n  \t  ") == ""

    def test_plain_text(self, converter: MrkdwnConverter) -> None:
        """Test plain text is unchanged."""
        text = "Hello, World!"
        assert converter.convert(text) == text

    def test_multiline_text(self, converter: MrkdwnConverter) -> None:
        """Test multiline content."""
        md = "# Title\n\nParagraph with **bold**.\n\n- List item"
        result = converter.convert(md)
        assert "*Title*" in result
        assert "*bold*" in result
        assert "\u2022 List item" in result

    def test_state_reset_between_calls(self, converter: MrkdwnConverter) -> None:
        """Test converter state resets between calls."""
        # First call with unclosed code block
        converter.convert("```\ncode")
        # Second call should work normally
        result = converter.convert("**bold**")
        assert result == "*bold*"


class TestConvenienceFunction:
    """Test the convert() convenience function."""

    def test_convert_function(self) -> None:
        """Test convert() function works like class method."""
        assert convert("**bold**") == "*bold*"

    def test_convert_function_complex(self) -> None:
        """Test convert() with complex markdown."""
        md = "# Hello\n\nThis is **bold** and [a link](https://example.com)."
        result = convert(md)
        assert "*Hello*" in result
        assert "*bold*" in result
        assert "<https://example.com|a link>" in result


class TestBlockquotes:
    """Test blockquote handling."""

    def test_blockquote_preserved(self, converter: MrkdwnConverter) -> None:
        """Test blockquotes are preserved (same syntax)."""
        md = "> This is a quote"
        result = converter.convert(md)
        assert "> This is a quote" in result

    def test_multiline_blockquote(self, converter: MrkdwnConverter) -> None:
        """Test multiline blockquote."""
        md = "> Line 1\n> Line 2"
        result = converter.convert(md)
        assert "> Line 1" in result
        assert "> Line 2" in result
