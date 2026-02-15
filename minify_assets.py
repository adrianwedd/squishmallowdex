#!/usr/bin/env python3
"""
Minify CSS and JavaScript files for better performance.
"""

import re
from pathlib import Path
import sys


def minify_css(css_content: str) -> str:
    """
    Simple CSS minification.

    Args:
        css_content: Original CSS content

    Returns:
        Minified CSS
    """
    # Remove comments
    css_content = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', css_content)

    # Remove whitespace
    css_content = re.sub(r'\s+', ' ', css_content)

    # Remove spaces around special characters
    css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)

    # Remove trailing semicolons
    css_content = re.sub(r';}', '}', css_content)

    return css_content.strip()


def minify_js(js_content: str) -> str:
    """
    Simple JavaScript minification (basic).
    For production, use proper tools like terser or uglify-js.

    Args:
        js_content: Original JS content

    Returns:
        Minified JS
    """
    # Remove single-line comments (but be careful with URLs)
    js_content = re.sub(r'(?<!:)//.*?$', '', js_content, flags=re.MULTILINE)

    # Remove multi-line comments
    js_content = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', js_content)

    # Remove excess whitespace (but preserve some for safety)
    js_content = re.sub(r'\n\s*\n', '\n', js_content)
    js_content = re.sub(r'  +', ' ', js_content)

    return js_content.strip()


def process_file(file_path: Path, output_dir: Path = None) -> bool:
    """
    Minify a CSS or JS file.

    Args:
        file_path: Path to the file
        output_dir: Optional output directory (default: same location with .min extension)

    Returns:
        True if successful
    """
    try:
        # Read original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        original_size = len(original_content)

        # Minify based on file type
        if file_path.suffix == '.css':
            minified_content = minify_css(original_content)
        elif file_path.suffix == '.js':
            minified_content = minify_js(original_content)
        else:
            print(f"  ❌ Unsupported file type: {file_path.suffix}")
            return False

        minified_size = len(minified_content)
        savings = ((original_size - minified_size) / original_size * 100) if original_size > 0 else 0

        # Determine output path
        if output_dir:
            output_path = output_dir / file_path.name
        else:
            # Add .min before extension
            output_path = file_path.with_name(f"{file_path.stem}.min{file_path.suffix}")

        # Write minified file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_content)

        print(f"  ✅ {file_path.name}: {original_size} → {minified_size} bytes ({savings:.1f}% saved)")
        print(f"     Output: {output_path}")

        return True

    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Minify CSS and JS files')
    parser.add_argument('files', nargs='*', help='Files or directories to process')
    parser.add_argument('--output', '-o', help='Output directory')

    args = parser.parse_args()

    # Default to current directory if no files specified
    if not args.files:
        # Look for CSS and JS files
        files = list(Path('.').glob('**/*.css')) + list(Path('.').glob('**/*.js'))
        # Filter out already minified files and node_modules
        files = [f for f in files if '.min.' not in f.name and 'node_modules' not in str(f)]
    else:
        files = []
        for file_arg in args.files:
            path = Path(file_arg)
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                files.extend(path.glob('**/*.css'))
                files.extend(path.glob('**/*.js'))

    if not files:
        print("No CSS or JS files found to minify")
        sys.exit(0)

    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(files)} file(s) to minify\n")

    processed = 0
    for file_path in files:
        if '.min.' in file_path.name:
            continue
        print(f"Processing: {file_path}")
        if process_file(file_path, output_dir):
            processed += 1

    print(f"\n{'='*60}")
    print(f"Minified {processed}/{len(files)} files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
