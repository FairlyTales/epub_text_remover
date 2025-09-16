#!/usr/bin/env python3
"""
EPUB Text Remover using ZIP approach
Remove specific text patterns from EPUB files by treating them as ZIP archives.

Example:
python epub_text_remover.py book.epub --remove "unwanted text"
python epub_text_remover.py book.epub --remove "pattern1" --remove "pattern2"
python epub_text_remover.py book.epub --regex --remove "Page \d+"
"""

import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup


class SimpleEPUBTextRemover:
    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_processed = []

    def log(self, message: str, level: str = "INFO"):
        """Print log message if verbose mode is enabled."""
        if self.verbose or level == "ERROR":
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def remove_text_from_html(
        self,
        content: str,
        patterns: List[str],
        use_regex: bool = False,
        case_sensitive: bool = True
    ) -> Tuple[str, int]:
        """Remove text patterns from HTML content."""
        soup = BeautifulSoup(content, 'html.parser')
        changes = 0

        for text_node in soup.find_all(string=True):
            original_text = str(text_node)
            modified_text = original_text

            for pattern in patterns:
                if use_regex:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    pattern_re = re.compile(pattern, flags)
                    matches = len(pattern_re.findall(modified_text))
                    if matches > 0:
                        modified_text = pattern_re.sub('', modified_text)
                        changes += matches
                        if self.verbose:
                            self.log(f"  Removed {matches} occurrences of regex: {pattern[:50]}...")
                else:
                    if case_sensitive:
                        count = modified_text.count(pattern)
                        if count > 0:
                            modified_text = modified_text.replace(pattern, '')
                            changes += count
                            if self.verbose:
                                self.log(f"  Removed {count} occurrences of: {pattern[:30]}...")
                    else:
                        pattern_lower = pattern.lower()
                        temp_text = modified_text
                        count = 0
                        pos = 0
                        while True:
                            lower_text = temp_text.lower()
                            index = lower_text.find(pattern_lower, pos)
                            if index == -1:
                                break
                            temp_text = temp_text[:index] + temp_text[index + len(pattern):]
                            count += 1
                        if count > 0:
                            modified_text = temp_text
                            changes += count
                            if self.verbose:
                                self.log(f"  Removed {count} occurrences (case-insensitive)")

            if modified_text != original_text:
                text_node.replace_with(modified_text)

        return str(soup), changes

    def process_epub_zip(
        self,
        input_path: Path,
        output_path: Optional[Path],
        patterns: List[str],
        use_regex: bool = False,
        case_sensitive: bool = True,
        backup: bool = True
    ) -> bool:
        """Process EPUB as a ZIP file."""
        try:
            self.log(f"Processing: {input_path.name}")

            if not zipfile.is_zipfile(input_path):
                self.log(f"Error: {input_path.name} is not a valid EPUB/ZIP file", "ERROR")
                return False

            total_changes = 0
            modified_files = []

            # Create a temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract EPUB contents
                with zipfile.ZipFile(input_path, 'r') as zip_in:
                    zip_in.extractall(temp_path)

                # Process HTML/XHTML files
                for html_file in temp_path.rglob('*.html'):
                    content = html_file.read_text(encoding='utf-8', errors='ignore')
                    modified_content, changes = self.remove_text_from_html(
                        content, patterns, use_regex, case_sensitive
                    )

                    if changes > 0:
                        total_changes += changes
                        modified_files.append(html_file.name)

                        if not self.dry_run:
                            html_file.write_text(modified_content, encoding='utf-8')

                        if self.verbose:
                            self.log(f"  Modified: {html_file.name} ({changes} changes)")

                for xhtml_file in temp_path.rglob('*.xhtml'):
                    content = xhtml_file.read_text(encoding='utf-8', errors='ignore')
                    modified_content, changes = self.remove_text_from_html(
                        content, patterns, use_regex, case_sensitive
                    )

                    if changes > 0:
                        total_changes += changes
                        modified_files.append(xhtml_file.name)

                        if not self.dry_run:
                            xhtml_file.write_text(modified_content, encoding='utf-8')

                        if self.verbose:
                            self.log(f"  Modified: {xhtml_file.name} ({changes} changes)")

                if total_changes == 0:
                    self.log("No matching text found to remove.")
                    return False

                self.log(f"Total changes: {total_changes} in {len(modified_files)} files")

                if self.dry_run:
                    self.log("DRY RUN: No files were actually modified.")
                    if modified_files:
                        self.log(f"Would modify: {', '.join(modified_files[:5])}" +
                                ("..." if len(modified_files) > 5 else ""))
                else:
                    # Backup original if requested
                    if backup:
                        backup_path = input_path.with_suffix('.epub.bak')
                        shutil.copy2(input_path, backup_path)
                        self.log(f"Backup saved: {backup_path.name}")

                    # Determine output path
                    if output_path is None:
                        output_path = input_path.with_name(
                            input_path.stem + '_cleaned' + input_path.suffix
                        )

                    # Create new EPUB
                    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                        for file_path in temp_path.rglob('*'):
                            if file_path.is_file():
                                arc_name = file_path.relative_to(temp_path)
                                zip_out.write(file_path, arc_name)

                    self.log(f"Output saved: {output_path.name}")
                    self.changes_made += total_changes
                    self.files_processed.append(str(output_path))

            return True

        except Exception as e:
            self.log(f"Error processing {input_path.name}: {str(e)}", "ERROR")
            return False

    def process_multiple(
        self,
        file_patterns: List[str],
        patterns: List[str],
        use_regex: bool = False,
        case_sensitive: bool = True,
        backup: bool = True,
        output_suffix: str = '_cleaned'
    ) -> int:
        """Process multiple EPUB files."""
        epub_files = []

        for pattern in file_patterns:
            path = Path(pattern)
            if path.is_file() and path.suffix.lower() == '.epub':
                epub_files.append(path)
            elif '*' in pattern or '?' in pattern:
                epub_files.extend(Path.cwd().glob(pattern))
            else:
                self.log(f"Warning: {pattern} is not a valid EPUB file", "WARNING")

        if not epub_files:
            self.log("No EPUB files found to process.", "ERROR")
            return 0

        self.log(f"Found {len(epub_files)} EPUB file(s) to process")

        successful = 0
        for epub_file in epub_files:
            output_path = None if output_suffix else epub_file.with_name(
                epub_file.stem + output_suffix + epub_file.suffix
            )

            if self.process_epub_zip(
                epub_file, output_path, patterns,
                use_regex, case_sensitive, backup
            ):
                successful += 1

            print()  # Empty line between files

        return successful


def main():
    parser = argparse.ArgumentParser(
        description='Remove text patterns from EPUB files (ZIP-based approach)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s book.epub --remove "unwanted text"
  %(prog)s book.epub --remove "pattern1" --remove "pattern2"
  %(prog)s "*.epub" --regex "Page \\d+"
  %(prog)s book.epub --remove "text" --case-insensitive
  %(prog)s book.epub --remove "text" --dry-run --verbose
        '''
    )

    parser.add_argument('files', nargs='+', help='EPUB file(s) to process')
    parser.add_argument('-r', '--remove', action='append', dest='patterns',
                       help='Text pattern to remove (can be specified multiple times)')
    parser.add_argument('--regex', action='store_true',
                       help='Treat patterns as regular expressions')
    parser.add_argument('-o', '--output', help='Output file path (single file only)')
    parser.add_argument('--output-suffix', default='_cleaned',
                       help='Suffix for output files (default: _cleaned)')
    parser.add_argument('--case-insensitive', action='store_false',
                       dest='case_sensitive', help='Case-insensitive matching')
    parser.add_argument('--no-backup', action='store_false',
                       dest='backup', help='Do not create backup files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed processing information')
    parser.add_argument('--remove-page-numbers', action='store_true',
                       help='Remove common page number patterns')

    args = parser.parse_args()

    if not args.patterns and not args.remove_page_numbers:
        parser.error('No patterns specified. Use --remove or --remove-page-numbers')

    if args.output and len(args.files) > 1:
        parser.error('--output can only be used with a single file')

    # Build pattern list
    patterns = args.patterns if args.patterns else []

    if args.remove_page_numbers:
        patterns.extend([
            r'Page\s+\d+',
            r'^\s*\d+\s*$',
            r'\[\s*\d+\s*\]',
        ])
        use_regex = True
    else:
        use_regex = args.regex

    # Process files
    remover = SimpleEPUBTextRemover(verbose=args.verbose, dry_run=args.dry_run)
    output_path = Path(args.output) if args.output else None

    successful = remover.process_multiple(
        args.files, patterns, use_regex,
        args.case_sensitive, args.backup, args.output_suffix
    )

    # Print summary
    print("\n" + "="*50)
    if remover.dry_run:
        print("DRY RUN SUMMARY")
        print(f"Would process: {successful} file(s)")
        print(f"Total changes: {remover.changes_made}")
    else:
        print("PROCESSING SUMMARY")
        print(f"Successfully processed: {successful} file(s)")
        print(f"Total changes made: {remover.changes_made}")
        if remover.files_processed:
            print("\nOutput files:")
            for file in remover.files_processed[:10]:
                print(f"  - {Path(file).name}")

    return 0 if successful > 0 else 1


if __name__ == '__main__':
    sys.exit(main())