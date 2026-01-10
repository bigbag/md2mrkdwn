# md2mrkdwn

[![CI](https://github.com/bigbag/md2mrkdwn/workflows/CI/badge.svg)](https://github.com/bigbag/md2mrkdwn/actions?query=workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/md2mrkdwn.svg)](https://pypi.python.org/pypi/md2mrkdwn)
[![downloads](https://img.shields.io/pypi/dm/md2mrkdwn.svg)](https://pypistats.org/packages/md2mrkdwn)
[![versions](https://img.shields.io/pypi/pyversions/md2mrkdwn.svg)](https://github.com/bigbag/md2mrkdwn)
[![license](https://img.shields.io/github/license/bigbag/md2mrkdwn.svg)](https://github.com/bigbag/md2mrkdwn/blob/master/LICENSE)

Pure Python library for converting Markdown to Slack's mrkdwn format. Zero dependencies, comprehensive formatting support, and proper handling of edge cases.

## Features

- **Zero dependencies** - Pure Python implementation with no external packages required
- **Comprehensive formatting** - Supports bold, italic, strikethrough, links, images, lists, and more
- **Configurable** - Customize symbols, formats, and enable/disable specific conversions
- **Code block handling** - Preserves content inside code blocks without conversion
- **Table support** - Wraps markdown tables in code blocks for Slack display
- **Task lists** - Converts checkbox syntax to Unicode symbols (☐/☑)
- **Edge case handling** - Properly handles nested formatting and special characters

## Quick Start

```python
from md2mrkdwn import convert

markdown = "**Hello** *World*! Check out [Slack](https://slack.com)"
mrkdwn = convert(markdown)
print(mrkdwn)
# Output: *Hello* _World_! Check out <https://slack.com|Slack>
```

## Installation

```bash
# Install with pip
pip install md2mrkdwn

# Or install with uv
uv add md2mrkdwn

# Or install with pipx (for CLI tools that use this library)
pipx install md2mrkdwn
```

## Usage

### Simple Function

The `convert()` function provides a simple interface for one-off conversions:

```python
from md2mrkdwn import convert

markdown = """
# Hello World

This is **bold** and *italic* text.

- Item 1
- Item 2

Check out [this link](https://example.com)!
"""

mrkdwn = convert(markdown)
print(mrkdwn)
```

Output:
```
*Hello World*

This is *bold* and _italic_ text.

• Item 1
• Item 2

Check out <https://example.com|this link>!
```

### Class-based Usage

For multiple conversions, use the `MrkdwnConverter` class:

```python
from md2mrkdwn import MrkdwnConverter

converter = MrkdwnConverter()

# Convert multiple texts
text1 = converter.convert("**bold** and *italic*")
text2 = converter.convert("# Header\n\n- List item")

print(text1)  # *bold* and _italic_
print(text2)  # *Header*\n\n• List item
```

### Custom Configuration

Use `MrkdwnConfig` to customize conversion behavior:

```python
from md2mrkdwn import convert, MrkdwnConfig, MrkdwnConverter

# Custom bullet character
config = MrkdwnConfig(bullet_char="-")
print(convert("- Item 1\n- Item 2", config=config))
# Output: - Item 1
#         - Item 2

# Custom checkbox symbols
config = MrkdwnConfig(checkbox_checked="✓", checkbox_unchecked="○")
print(convert("- [x] Done\n- [ ] Todo", config=config))
# Output: • ✓ Done
#         • ○ Todo

# Plain headers (no bold)
config = MrkdwnConfig(header_style="plain")
print(convert("# Title", config=config))
# Output: Title

# URL-only links (no link text)
config = MrkdwnConfig(link_format="url_only")
print(convert("[Click here](https://example.com)", config=config))
# Output: <https://example.com>

# Disable specific conversions
config = MrkdwnConfig(convert_bold=False, convert_italic=False)
print(convert("**bold** and *italic*", config=config))
# Output: **bold** and *italic*

# Reusable converter with config
converter = MrkdwnConverter(MrkdwnConfig(
    bullet_char="→",
    horizontal_rule_char="=",
    horizontal_rule_length=20
))
print(converter.convert("- Item\n\n---"))
# Output: → Item
#
#         ====================
```

### Configuration Options

| Option                     | Type | Default        | Description                               |
|----------------------------|------|----------------|-------------------------------------------|
| `bullet_char`              | str  | `•`            | Character for unordered list items        |
| `checkbox_checked`         | str  | `☑`            | Symbol for checked task items             |
| `checkbox_unchecked`       | str  | `☐`            | Symbol for unchecked task items           |
| `horizontal_rule_char`     | str  | `─`            | Character for horizontal rules            |
| `horizontal_rule_length`   | int  | `10`           | Length of horizontal rules                |
| `header_style`             | str  | `"bold"`       | `"bold"`, `"plain"`, or `"prefix"`        |
| `link_format`              | str  | `"slack"`      | `"slack"`, `"url_only"`, or `"text_only"` |
| `table_mode`               | str  | `"code_block"` | `"code_block"` or `"preserve"`            |
| `convert_bold`             | bool | `True`         | Enable/disable bold conversion            |
| `convert_italic`           | bool | `True`         | Enable/disable italic conversion          |
| `convert_strikethrough`    | bool | `True`         | Enable/disable strikethrough conversion   |
| `convert_links`            | bool | `True`         | Enable/disable link conversion            |
| `convert_images`           | bool | `True`         | Enable/disable image conversion           |
| `convert_lists`            | bool | `True`         | Enable/disable list conversion            |
| `convert_task_lists`       | bool | `True`         | Enable/disable task list conversion       |
| `convert_headers`          | bool | `True`         | Enable/disable header conversion          |
| `convert_horizontal_rules` | bool | `True`         | Enable/disable horizontal rule conversion |
| `convert_tables`           | bool | `True`         | Enable/disable table wrapping             |

### Handling Tables

Markdown tables are automatically wrapped in code blocks since Slack doesn't support native table rendering:

```python
from md2mrkdwn import convert

markdown = """
| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
"""

print(convert(markdown))
```

Output:
```
```
| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
```
```

## Conversion Reference

| Markdown                   | mrkdwn             | Notes                        |
|----------------------------|--------------------|------------------------------|
| `**bold**` or `__bold__`   | `*bold*`           | Slack uses single asterisk   |
| `*italic*` or `_italic_`   | `_italic_`         | Slack uses underscores       |
| `***bold+italic***`        | `*_text_*`         | Combined formatting          |
| `~~strikethrough~~`        | `~text~`           | Single tilde                 |
| `[text](url)`              | `<url\|text>`      | Slack link format            |
| `![alt](url)`              | `<url>`            | Images become plain URLs     |
| `# Header` (all levels)    | `*Header*`         | Bold (Slack has no headers)  |
| `- item` / `* item`        | `• item`           | Bullet character (U+2022)    |
| `1. item`                  | `1. item`          | Preserved as-is              |
| `- [ ] task`               | `• ☐ task`         | Unchecked checkbox (U+2610)  |
| `- [x] task`               | `• ☑ task`         | Checked checkbox (U+2611)    |
| `> quote`                  | `> quote`          | Same syntax                  |
| `` `code` ``               | `` `code` ``       | Same syntax                  |
| ``` code block ```         | ``` code block ``` | Same syntax                  |
| `---` / `***`              | `──────────`       | Horizontal rule (U+2500)     |
| Tables                     | Wrapped in ```     | Slack has no native tables   |

## How It Works

### Conversion Pipeline

md2mrkdwn processes text through a multi-stage pipeline:

1. **Table extraction** - Tables are detected, validated, and replaced with placeholders
2. **Code block tracking** - Lines inside code blocks are skipped during conversion
3. **Pattern application** - Regex patterns convert formatting using placeholder protection
4. **Placeholder restoration** - Tables and temporary markers are replaced with final output

### Pattern Interference Prevention

A key challenge in markdown conversion is preventing patterns from interfering with each other. For example, converting `**bold**` to `*bold*` could then be matched by the italic pattern.

md2mrkdwn solves this using placeholder substitution:
1. Bold text is temporarily marked with null-byte placeholders
2. Italic patterns run without matching the placeholders
3. Placeholders are replaced with final mrkdwn characters

### Table Handling

Tables are detected using these criteria:
- Lines matching `|...|` pattern
- Second row contains separator cells (dashes with optional alignment colons)
- Header and separator have matching column counts

Valid tables are wrapped in triple-backtick code blocks for monospace display in Slack.

### Code Block Protection

Content inside code blocks (both fenced and inline) is protected from conversion:
- Fenced blocks: State machine tracks opening/closing ``` markers
- Inline code: Segments are extracted before conversion and restored after

## Development

### Setup

```bash
git clone https://github.com/bigbag/md2mrkdwn.git
cd md2mrkdwn
make install
```

### Commands

```bash
make install  # Install all dependencies
make test     # Run tests with coverage
make lint     # Run linters (ruff + mypy)
make format   # Format code with ruff
make clean    # Clean cache and build files
```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest --cov=md2mrkdwn --cov-report=term-missing

# Run specific test class
uv run pytest tests/test_converter.py::TestBasicFormatting -v

# Run with verbose output
uv run pytest -v
```

### Project Structure

```
md2mrkdwn/
├── src/
│   └── md2mrkdwn/
│       ├── __init__.py      # Package exports
│       └── converter.py     # MrkdwnConverter, MrkdwnConfig classes
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_converter.py    # Converter tests
│   └── test_config.py       # Configuration tests
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md
```

## API Reference

### `convert(markdown: str, config: MrkdwnConfig | None = None) -> str`

Convert Markdown text to Slack mrkdwn format.

**Parameters:**
- `markdown` - Input text in Markdown format
- `config` - Optional configuration (uses defaults if not provided)

**Returns:**
- Text converted to Slack mrkdwn format

### `MrkdwnConverter`

Class for converting Markdown to mrkdwn.

**Constructor:**
- `MrkdwnConverter(config: MrkdwnConfig | None = None)`

**Methods:**
- `convert(markdown: str) -> str` - Convert Markdown text to mrkdwn

**Example:**
```python
converter = MrkdwnConverter()
result = converter.convert("**Hello** *World*")

# With custom config
config = MrkdwnConfig(bullet_char="-")
converter = MrkdwnConverter(config)
result = converter.convert("- Item")
```

### `MrkdwnConfig`

Immutable configuration dataclass for customizing conversion behavior.

**Example:**
```python
from md2mrkdwn import MrkdwnConfig, DEFAULT_CONFIG

# Create custom config
config = MrkdwnConfig(
    bullet_char="→",
    header_style="plain",
    convert_bold=False
)

# Use the default config singleton
print(DEFAULT_CONFIG.bullet_char)  # •
```


## See Also

- [Slack mrkdwn specification](https://api.slack.com/reference/surfaces/formatting) - Official Slack formatting documentation
- [markdown_to_mrkdwn](https://github.com/fla9ua/markdown_to_mrkdwn) - Related project for markdown to mrkdwn conversion

## License

MIT License - see [LICENSE](LICENSE) file.
