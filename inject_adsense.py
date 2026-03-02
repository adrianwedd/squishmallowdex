#!/usr/bin/env python3
"""
Inject Google AdSense script into HTML files.
Usage: python inject_adsense.py [file_or_directory]
"""

import sys
import os
from pathlib import Path

ADSENSE_SCRIPT = '''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5242622588206425"
     crossorigin="anonymous"></script>'''


def inject_adsense(html_content: str) -> str:
    """
    Inject AdSense script into the <head> section of HTML.

    Args:
        html_content: The original HTML content

    Returns:
        Modified HTML with AdSense script injected
    """
    # Check if AdSense is already present
    if 'pagead2.googlesyndication.com' in html_content:
        print("  ⚠️  AdSense script already present, skipping")
        return html_content

    # Find the <head> tag and inject after it
    if '<head>' in html_content:
        return html_content.replace('<head>', f'<head>\n{ADSENSE_SCRIPT}', 1)
    elif '<HEAD>' in html_content:
        return html_content.replace('<HEAD>', f'<HEAD>\n{ADSENSE_SCRIPT}', 1)
    else:
        print("  ❌ No <head> tag found")
        return html_content


def process_file(file_path: Path) -> bool:
    """
    Process a single HTML file.

    Args:
        file_path: Path to the HTML file

    Returns:
        True if file was modified, False otherwise
    """
    print(f"Processing: {file_path}")

    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Inject AdSense
        modified_content = inject_adsense(original_content)

        # Only write if content changed
        if modified_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"  ✅ AdSense injected successfully")
            return True
        else:
            return False

    except FileNotFoundError:
        print(f"  ❌ File not found: {file_path}")
        return False
    except PermissionError:
        print(f"  ❌ Permission denied: {file_path}")
        return False
    except UnicodeDecodeError as e:
        print(f"  ❌ Encoding error: {e}")
        return False
    except OSError as e:
        print(f"  ❌ I/O error: {e}")
        return False


def main():
    """Main function to process HTML files."""
    if len(sys.argv) < 2:
        # Default: process squishmallowdex.html
        target = Path("squishmallowdex.html")
    else:
        target = Path(sys.argv[1])

    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)

    files_processed = 0
    files_modified = 0

    if target.is_file():
        # Process single file
        if target.suffix.lower() == '.html':
            files_processed = 1
            if process_file(target):
                files_modified = 1
        else:
            print(f"Error: {target} is not an HTML file")
            sys.exit(1)
    elif target.is_dir():
        # Process directory
        html_files = list(target.glob('*.html'))

        if not html_files:
            print(f"No HTML files found in {target}")
            sys.exit(1)

        for html_file in html_files:
            files_processed += 1
            if process_file(html_file):
                files_modified += 1

    print(f"\n{'='*60}")
    print(f"Summary: {files_modified}/{files_processed} files modified")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
