#!/usr/bin/env python3
"""
Inject Google Analytics (gtag.js) script into HTML files.
Usage: python inject_analytics.py [file_or_directory]
"""

import sys
import os
from pathlib import Path

ANALYTICS_SCRIPT = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-MLCG3SLHC2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-MLCG3SLHC2');
</script>'''


def inject_analytics(html_content: str) -> str:
    """
    Inject Google Analytics script into the <head> section of HTML.

    Args:
        html_content: The original HTML content

    Returns:
        Modified HTML with Analytics script injected
    """
    # Check if Analytics is already present
    if 'G-MLCG3SLHC2' in html_content or 'googletagmanager.com/gtag/js' in html_content:
        print("  ⚠️  Google Analytics already present, skipping")
        return html_content

    # Find the <head> tag and inject after it
    if '<head>' in html_content:
        return html_content.replace('<head>', f'<head>\n{ANALYTICS_SCRIPT}', 1)
    elif '<HEAD>' in html_content:
        return html_content.replace('<HEAD>', f'<HEAD>\n{ANALYTICS_SCRIPT}', 1)
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

        # Inject Analytics
        modified_content = inject_analytics(original_content)

        # Only write if content changed
        if modified_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"  ✅ Google Analytics injected successfully")
            return True
        else:
            return False

    except Exception as e:
        print(f"  ❌ Error processing file: {e}")
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
