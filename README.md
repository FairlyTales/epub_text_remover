# EPUB Text Remover

A Python script for removing unwanted text patterns from EPUB files by treating them as ZIP archives. Perfect for cleaning up ebooks by removing page numbers, watermarks, or any other unwanted text.

## Features

- Remove specific text patterns from EPUB files
- Support for regular expressions
- Case-sensitive and case-insensitive matching
- Batch processing of multiple files
- Dry-run mode for previewing changes
- Automatic backup creation
- Verbose logging for detailed processing information
- Built-in page number removal patterns

## Requirements

- Python 3.6+
- Required packages: `beautifulsoup4`

Install dependencies:

```bash
pip install beautifulsoup4
```

## Usage

### Basic Usage

Remove specific text from an EPUB file:

```bash
python epub_text_remover.py book.epub --remove "unwanted text"
```

### Multiple Patterns

Remove multiple text patterns:

```bash
python epub_text_remover.py book.epub --remove "pattern1" --remove "pattern2"
```

### Regular Expressions

Use regular expressions for pattern matching:

```bash
python epub_text_remover.py book.epub --regex --remove "Page \d+"
```

### Case-Insensitive Matching

Perform case-insensitive text removal:

```bash
python epub_text_remover.py book.epub --remove "text" --case-insensitive
```

### Batch Processing

Process multiple EPUB files at once:

```bash
python epub_text_remover.py *.epub --remove "unwanted text"
python epub_text_remover.py book1.epub book2.epub --remove "pattern"
```

### Quick Page Number Removal

Remove common page number patterns automatically:

```bash
python epub_text_remover.py book.epub --remove-page-numbers
```

### Dry Run Mode

Preview changes without modifying files:

```bash
python epub_text_remover.py book.epub --remove "text" --dry-run --verbose
```

## Command Line Options

| Option                  | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `files`                 | EPUB file(s) to process (required)                  |
| `-r, --remove`          | Text pattern to remove (can be used multiple times) |
| `--regex`               | Treat patterns as regular expressions               |
| `-o, --output`          | Output file path (single file only)                 |
| `--output-suffix`       | Suffix for output files (default: `_cleaned`)       |
| `--case-insensitive`    | Enable case-insensitive matching                    |
| `--no-backup`           | Do not create backup files                          |
| `--dry-run`             | Preview changes without modifying files             |
| `-v, --verbose`         | Show detailed processing information                |
| `--remove-page-numbers` | Remove common page number patterns                  |

## Examples

1. **Remove watermarks from an ebook:**

   ```bash
   python epub_text_remover.py book.epub --remove "Watermark | some_webpage.com"
   ```

2. **Remove page numbers using regex:**

   ```bash
   python epub_text_remover.py book.epub --regex --remove "Page \d+"
   ```

3. **Clean multiple books with verbose output:**

   ```bash
   python epub_text_remover.py *.epub --remove-page-numbers --verbose
   ```

4. **Preview changes before processing:**

   ```bash
   python epub_text_remover.py book.epub --remove "unwanted" --dry-run --verbose
   ```

5. **Process with custom output filename:**
   ```bash
   python epub_text_remover.py book.epub --remove "text" --output clean_book.epub
   ```

## Output

- By default, processed files are saved with `_cleaned` suffix
- Original files are automatically backed up with `.bak` extension (unless `--no-backup` is used)
- The script provides a summary of changes made and files processed

## EPUB to FB2 Conversion

This repository also includes a bash script for converting EPUB files to FB2 format using Calibre.

### Requirements for Conversion

- [Calibre](https://calibre-ebook.com/) must be installed on your system
- The script assumes Calibre is installed in the default macOS location: `/Applications/calibre.app/Contents/MacOS/ebook-convert`

### Usage

1. **Place the script in the directory containing your EPUB files**

2. **Make the script executable:**

   ```bash
   chmod +x epub_to_fb2_convert.sh
   ```

3. **Run the conversion:**
   ```bash
   ./epub_to_fb2_convert.sh
   ```

### What the Script Does

- Automatically finds all `.epub` files in the current directory
- Creates a `fb2_converted` directory for output files
- Converts each EPUB file to FB2 format using Calibre's `ebook-convert` tool
- Shows progress with a counter (`[1/5] Converting: book.epub`)
- Provides success/failure feedback for each conversion
- Displays a final summary of successful conversions

### Example Output

```
Starting conversion of 3 EPUB files to FB2 format...
============================================
[1/3] Converting: book1.epub
  ✓ Successfully converted to: fb2_converted/book1.fb2

[2/3] Converting: book2.epub
  ✓ Successfully converted to: fb2_converted/book2.fb2

[3/3] Converting: book3.epub
  ✓ Successfully converted to: fb2_converted/book3.fb2

============================================
Conversion complete!
Converted files are in the 'fb2_converted' directory
Successfully converted: 3 out of 3 files
```

### Workflow Recommendation

For best results when cleaning ebooks:

1. **First, clean the EPUB files:**

   ```bash
   python epub_text_remover.py *.epub --remove-page-numbers --verbose
   ```

2. **Then convert the cleaned files to FB2:**
   ```bash
   ./epub_to_fb2_convert.sh
   ```

This ensures your FB2 files are free of unwanted text patterns like page numbers and watermarks.

## Notes

- The script processes HTML and XHTML files within the EPUB
- Text is removed while preserving the HTML structure
- Regular expressions follow Python's `re` module syntax
- Use `--dry-run` to safely test patterns before applying changes
