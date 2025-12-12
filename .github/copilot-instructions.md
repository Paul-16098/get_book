# Get Book - AI Copilot Instructions

## Project Overview

**Get Book** is a Python CLI tool that manages book collections and opens browser searches across multiple novel/book websites simultaneously. It combines JSON-based data persistence with URL parameter formatting to streamline the workflow of tracking and discovering books across multiple sources.

### Architecture

- **Data Layer**: JSON files in `web-data/` define search websites; `book-name.json` stores pending books
- **Core Classes**:
  - `WebData`: Single website with name and parameterized URL template
  - `WebDataList`: Collection of websites; loads from `web-data/*.json` and opens all matching searches
  - `BookDataList`: Book queue with persistence; intelligently parses copy-paste data containing keywords like "有更新" (updated), "尚未閱讀" (unread), "無更新" (no update)
- **Workflow**: Input → Load existing books → Accept stdin/interactive input → Process books sequentially → Open all website searches → Remove from queue

## Key Patterns

### Data Formatting & URL Templates

WebData uses Python's `.format()` with flexible argument handling:

```python
# From web-data/Twkan.json:
{"name": "臺灣小說網", "web": "https://twkan.com/search/{q}/1.html"}

# Usage:
web_data.get({"q": "book_title"})        # dict kwargs
web_data.get("book_title")               # positional args
web_data.open({"q": "book_title"})       # opens URL in browser
web_data_list.open_all({"q": "book"})    # opens all websites with same book
```

### Intelligent Text Parsing

`BookDataList.text_to_data()` extracts book names from copy-pasted data:

```python
# Input: "  無更新 小說名稱   \n  有更新 另一本書  "
# Extracts: ["小說名稱"] (takes the word AFTER the keyword)

# Keyword detection in is_data_text():
if any(keyword in data_text for keyword in ["有更新", "尚未閱讀", "無更新"]):
```

This allows direct pasting from spreadsheets or status lists.

### Persistence & Partial Processing

- Books load from both `book-name.json` and `book-name.d.json` (draft file, optional)
- After processing each book, file is immediately rewritten with book removed (`pop(0)`)
- Interrupting mid-process (Ctrl+C) safely persists progress
- `safe_remove()` prevents errors when file doesn't exist

## Development Workflow

### Running

```bash
python get_book.py
```

Expects JSON array from stdin (e.g., `echo '["book1", "book2"]' | python get_book.py`)

### Testing

```bash
cargo nextest run        # Primary test runner
sg test --interactive   # ast-grep pattern matching tests
```

### Adding a New Website

1. Create `web-data/<site_name>.json`:
   ```json
   { "name": "Display Name", "web": "https://site.com/search/{q}" }
   ```
2. Add any needed placeholders (e.g., `{q}` for query, `{id}` for ID)
3. Run script; site auto-loads via `glob.glob("./web-data/*.json")`

### Code Organization Notes

- Uses `loguru` for logging (imported but config not in this file)
- Requires `paul-tools>=1.0.7` dependency
- Chinese comments throughout; maintain bilingual style for future contributors
- TypedDict usage (`WebDataType`) documents expected JSON structure
- Commented-out `cofg` field suggests future config/feature expansion

## Common Pitfalls

- **JSON decode errors**: Ensure `book-name.json` contains valid JSON array; script auto-creates if missing
- **File encoding**: Always use `encoding="utf-8"` when opening files (Chinese character support)
- **stdin handling**: Script reads all stdin at start; piping data required for non-interactive use
- **URL formatting failures**: `WebData.get()` catches `KeyError` silently and returns unformatted URL

## Dependencies

- **loguru**: Structured logging with debug/info/error levels
- **paul-tools**: External utility library (version ≥1.0.7)
- **Python ≥3.13**: Required by pyproject.toml
