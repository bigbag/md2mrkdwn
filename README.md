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

| Markdown | mrkdwn | Notes |
|----------|--------|-------|
| `**bold**` or `__bold__` | `*bold*` | Slack uses single asterisk |
| `*italic*` or `_italic_` | `_italic_` | Slack uses underscores |
| `***bold+italic***` | `*_text_*` | Combined formatting |
| `~~strikethrough~~` | `~text~` | Single tilde |
| `[text](url)` | `<url\|text>` | Slack link format |
| `![alt](url)` | `<url>` | Images become plain URLs |
| `# Header` (all levels) | `*Header*` | Bold (Slack has no headers) |
| `- item` / `* item` | `• item` | Bullet character (U+2022) |
| `1. item` | `1. item` | Preserved as-is |
| `- [ ] task` | `• ☐ task` | Unchecked checkbox (U+2610) |
| `- [x] task` | `• ☑ task` | Checked checkbox (U+2611) |
| `> quote` | `> quote` | Same syntax |
| `` `code` `` | `` `code` `` | Same syntax |
| ``` code block ``` | ``` code block ``` | Same syntax |
| `---` / `***` | `──────────` | Horizontal rule (U+2500) |
| Tables | Wrapped in ``` | Slack has no native tables |

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
│       └── converter.py     # MrkdwnConverter class
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_converter.py    # Test suite (49 tests)
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md
```

## API Reference

### `convert(markdown: str) -> str`

Convert Markdown text to Slack mrkdwn format.

**Parameters:**
- `markdown` - Input text in Markdown format

**Returns:**
- Text converted to Slack mrkdwn format

### `MrkdwnConverter`

Class for converting Markdown to mrkdwn.

**Methods:**
- `convert(markdown: str) -> str` - Convert Markdown text to mrkdwn

**Example:**
```python
converter = MrkdwnConverter()
result = converter.convert("**Hello** *World*")
```

## License

MIT License - see [LICENSE](LICENSE) file.
