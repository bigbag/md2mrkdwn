"""Tests for MrkdwnConfig configuration class."""

import pytest

from md2mrkdwn import DEFAULT_CONFIG, MrkdwnConfig, MrkdwnConverter, convert


class TestMrkdwnConfigDefaults:
    """Test default configuration values."""

    def test_default_bullet_char(self) -> None:
        config = MrkdwnConfig()
        assert config.bullet_char == "•"

    def test_default_checkbox_chars(self) -> None:
        config = MrkdwnConfig()
        assert config.checkbox_checked == "☑"
        assert config.checkbox_unchecked == "☐"

    def test_default_horizontal_rule(self) -> None:
        config = MrkdwnConfig()
        assert config.horizontal_rule_char == "─"
        assert config.horizontal_rule_length == 10

    def test_default_modes(self) -> None:
        config = MrkdwnConfig()
        assert config.header_style == "bold"
        assert config.link_format == "slack"
        assert config.table_mode == "code_block"

    def test_all_conversions_enabled_by_default(self) -> None:
        config = MrkdwnConfig()
        assert config.convert_bold is True
        assert config.convert_italic is True
        assert config.convert_strikethrough is True
        assert config.convert_links is True
        assert config.convert_images is True
        assert config.convert_lists is True
        assert config.convert_task_lists is True
        assert config.convert_headers is True
        assert config.convert_horizontal_rules is True
        assert config.convert_tables is True

    def test_default_config_matches_fresh_instance(self) -> None:
        assert MrkdwnConfig() == DEFAULT_CONFIG


class TestMrkdwnConfigValidation:
    """Test configuration validation."""

    def test_invalid_header_style(self) -> None:
        with pytest.raises(ValueError, match="header_style must be one of"):
            MrkdwnConfig(header_style="invalid")

    def test_invalid_link_format(self) -> None:
        with pytest.raises(ValueError, match="link_format must be one of"):
            MrkdwnConfig(link_format="invalid")

    def test_invalid_table_mode(self) -> None:
        with pytest.raises(ValueError, match="table_mode must be one of"):
            MrkdwnConfig(table_mode="invalid")

    def test_invalid_horizontal_rule_length_zero(self) -> None:
        with pytest.raises(ValueError, match="horizontal_rule_length must be at least 1"):
            MrkdwnConfig(horizontal_rule_length=0)

    def test_invalid_horizontal_rule_length_negative(self) -> None:
        with pytest.raises(ValueError, match="horizontal_rule_length must be at least 1"):
            MrkdwnConfig(horizontal_rule_length=-1)


class TestMrkdwnConfigImmutability:
    """Test that config is immutable."""

    def test_frozen_dataclass(self) -> None:
        config = MrkdwnConfig()
        with pytest.raises(AttributeError):
            config.bullet_char = "-"  # type: ignore[misc]


class TestConfiguredBulletChar:
    """Test custom bullet character."""

    def test_custom_bullet(self) -> None:
        config = MrkdwnConfig(bullet_char="-")
        converter = MrkdwnConverter(config)
        assert converter.convert("- Item") == "- Item"

    def test_custom_bullet_arrow(self) -> None:
        config = MrkdwnConfig(bullet_char="→")
        converter = MrkdwnConverter(config)
        assert converter.convert("- Item") == "→ Item"

    def test_custom_bullet_with_asterisk_list(self) -> None:
        config = MrkdwnConfig(bullet_char="*")
        converter = MrkdwnConverter(config)
        assert converter.convert("* Item") == "* Item"


class TestConfiguredCheckboxChars:
    """Test custom checkbox characters."""

    def test_custom_checkbox_chars(self) -> None:
        config = MrkdwnConfig(
            checkbox_checked="[x]",
            checkbox_unchecked="[ ]",
        )
        converter = MrkdwnConverter(config)
        assert "• [x]" in converter.convert("- [x] Done")
        assert "• [ ]" in converter.convert("- [ ] Todo")

    def test_custom_checkbox_with_custom_bullet(self) -> None:
        config = MrkdwnConfig(
            bullet_char="-",
            checkbox_checked="✓",
            checkbox_unchecked="○",
        )
        converter = MrkdwnConverter(config)
        assert "- ✓" in converter.convert("- [x] Done")
        assert "- ○" in converter.convert("- [ ] Todo")


class TestConfiguredHorizontalRule:
    """Test custom horizontal rule."""

    def test_custom_hr_char(self) -> None:
        config = MrkdwnConfig(horizontal_rule_char="=")
        converter = MrkdwnConverter(config)
        assert converter.convert("---") == "=" * 10

    def test_custom_hr_length(self) -> None:
        config = MrkdwnConfig(horizontal_rule_length=20)
        converter = MrkdwnConverter(config)
        assert converter.convert("---") == "─" * 20

    def test_custom_hr_both(self) -> None:
        config = MrkdwnConfig(horizontal_rule_char="*", horizontal_rule_length=5)
        converter = MrkdwnConverter(config)
        assert converter.convert("---") == "*****"


class TestConfiguredHeaderStyle:
    """Test header style options."""

    def test_header_style_bold(self) -> None:
        config = MrkdwnConfig(header_style="bold")
        converter = MrkdwnConverter(config)
        assert converter.convert("# Title") == "*Title*"

    def test_header_style_plain(self) -> None:
        config = MrkdwnConfig(header_style="plain")
        converter = MrkdwnConverter(config)
        assert converter.convert("# Title") == "Title"

    def test_header_style_prefix(self) -> None:
        config = MrkdwnConfig(header_style="prefix")
        converter = MrkdwnConverter(config)
        assert converter.convert("# Title") == "# Title"

    def test_header_style_h2(self) -> None:
        config = MrkdwnConfig(header_style="plain")
        converter = MrkdwnConverter(config)
        assert converter.convert("## Subtitle") == "Subtitle"


class TestConfiguredLinkFormat:
    """Test link format options."""

    def test_link_format_slack(self) -> None:
        config = MrkdwnConfig(link_format="slack")
        converter = MrkdwnConverter(config)
        assert converter.convert("[text](https://example.com)") == "<https://example.com|text>"

    def test_link_format_url_only(self) -> None:
        config = MrkdwnConfig(link_format="url_only")
        converter = MrkdwnConverter(config)
        assert converter.convert("[text](https://example.com)") == "<https://example.com>"

    def test_link_format_text_only(self) -> None:
        config = MrkdwnConfig(link_format="text_only")
        converter = MrkdwnConverter(config)
        assert converter.convert("[text](https://example.com)") == "text"


class TestConfiguredTableMode:
    """Test table mode options."""

    def test_table_mode_code_block(self) -> None:
        config = MrkdwnConfig(table_mode="code_block")
        converter = MrkdwnConverter(config)
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        assert "```" in converter.convert(md)

    def test_table_mode_preserve(self) -> None:
        config = MrkdwnConfig(table_mode="preserve")
        converter = MrkdwnConverter(config)
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = converter.convert(md)
        assert "```" not in result
        assert "| A | B |" in result


class TestDisabledConversions:
    """Test disabling specific conversions."""

    def test_disable_bold(self) -> None:
        config = MrkdwnConfig(convert_bold=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("**bold**") == "**bold**"

    def test_disable_italic(self) -> None:
        config = MrkdwnConfig(convert_italic=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("*italic*") == "*italic*"

    def test_disable_strikethrough(self) -> None:
        config = MrkdwnConfig(convert_strikethrough=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("~~strike~~") == "~~strike~~"

    def test_disable_links(self) -> None:
        config = MrkdwnConfig(convert_links=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("[text](url)") == "[text](url)"

    def test_disable_images(self) -> None:
        config = MrkdwnConfig(convert_images=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("![alt](url)") == "![alt](url)"

    def test_disable_lists(self) -> None:
        config = MrkdwnConfig(convert_lists=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("- Item") == "- Item"

    def test_disable_task_lists(self) -> None:
        config = MrkdwnConfig(convert_task_lists=False)
        converter = MrkdwnConverter(config)
        # Task list syntax becomes regular bullet when task_lists disabled
        result = converter.convert("- [x] Done")
        assert "☑" not in result
        assert "•" in result

    def test_disable_headers(self) -> None:
        config = MrkdwnConfig(convert_headers=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("# Title") == "# Title"

    def test_disable_horizontal_rules(self) -> None:
        config = MrkdwnConfig(convert_horizontal_rules=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("---") == "---"

    def test_disable_tables(self) -> None:
        config = MrkdwnConfig(convert_tables=False)
        converter = MrkdwnConverter(config)
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = converter.convert(md)
        assert "```" not in result
        assert "| A | B |" in result


class TestDisabledBoldItalicCombinations:
    """Test combinations of disabled bold/italic."""

    def test_disable_bold_keep_italic(self) -> None:
        config = MrkdwnConfig(convert_bold=False, convert_italic=True)
        converter = MrkdwnConverter(config)
        # Bold+italic becomes just italic
        assert converter.convert("***text***") == "_text_"
        # Regular italic still works
        assert converter.convert("*text*") == "_text_"
        # Bold stays as-is
        assert converter.convert("**text**") == "**text**"

    def test_disable_italic_keep_bold(self) -> None:
        config = MrkdwnConfig(convert_bold=True, convert_italic=False)
        converter = MrkdwnConverter(config)
        # Bold+italic becomes just bold
        assert converter.convert("***text***") == "*text*"
        # Regular bold still works
        assert converter.convert("**text**") == "*text*"
        # Italic stays as-is
        assert converter.convert("*text*") == "*text*"

    def test_disable_both_bold_and_italic(self) -> None:
        config = MrkdwnConfig(convert_bold=False, convert_italic=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("***text***") == "***text***"
        assert converter.convert("**text**") == "**text**"
        assert converter.convert("*text*") == "*text*"


class TestConvenienceFunctionWithConfig:
    """Test convert() function with config parameter."""

    def test_convert_with_config(self) -> None:
        config = MrkdwnConfig(bullet_char="-")
        result = convert("- Item", config=config)
        assert result == "- Item"

    def test_convert_without_config(self) -> None:
        # Should use default config
        result = convert("- Item")
        assert "•" in result

    def test_convert_with_multiple_options(self) -> None:
        config = MrkdwnConfig(
            bullet_char="→",
            header_style="plain",
            link_format="text_only",
        )
        md = "# Title\n\n- Item\n\n[link](url)"
        result = convert(md, config=config)
        assert "Title" in result
        assert "*Title*" not in result  # Not bold
        assert "→ Item" in result
        assert result.strip().endswith("link")


class TestBackwardCompatibility:
    """Ensure no changes to default behavior."""

    def test_default_bold(self) -> None:
        assert convert("**bold**") == "*bold*"

    def test_default_italic(self) -> None:
        assert convert("*italic*") == "_italic_"

    def test_default_bold_italic(self) -> None:
        assert convert("***bold italic***") == "*_bold italic_*"

    def test_default_strikethrough(self) -> None:
        assert convert("~~strike~~") == "~strike~"

    def test_default_link(self) -> None:
        assert convert("[text](https://example.com)") == "<https://example.com|text>"

    def test_default_image(self) -> None:
        assert convert("![alt](https://example.com/img.png)") == "<https://example.com/img.png>"

    def test_default_list(self) -> None:
        assert "•" in convert("- Item")

    def test_default_task_list(self) -> None:
        assert "☑" in convert("- [x] Done")
        assert "☐" in convert("- [ ] Todo")

    def test_default_header(self) -> None:
        assert convert("# Title") == "*Title*"

    def test_default_horizontal_rule(self) -> None:
        assert convert("---") == "─" * 10

    def test_default_table(self) -> None:
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        assert "```" in convert(md)


class TestConverterWithConfig:
    """Test MrkdwnConverter class with config."""

    def test_converter_default_config(self) -> None:
        converter = MrkdwnConverter()
        assert converter.convert("**bold**") == "*bold*"

    def test_converter_custom_config(self) -> None:
        config = MrkdwnConfig(convert_bold=False)
        converter = MrkdwnConverter(config)
        assert converter.convert("**bold**") == "**bold**"

    def test_converter_reuse_with_config(self) -> None:
        config = MrkdwnConfig(bullet_char="*")
        converter = MrkdwnConverter(config)
        assert converter.convert("- A") == "* A"
        assert converter.convert("- B") == "* B"
