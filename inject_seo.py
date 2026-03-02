#!/usr/bin/env python3
"""
Inject comprehensive SEO meta tags into HTML files.
Usage: python inject_seo.py [file_or_directory] [--url YOUR_URL]
"""

import sys
import os
import re
from pathlib import Path

# Default configuration - customize these
DEFAULT_CONFIG = {
    'url': 'https://squishmallowdex.com',  # Change to your actual domain
    'title': 'Squishmallowdex - Complete Squishmallows Collection & Database',
    'description': 'Discover and explore the complete Squishmallows collection! Search through thousands of adorable Squishmallows plushies, find rare characters, learn about new releases, and build your perfect collection.',
    'keywords': 'squishmallows, squishmallow, plush toys, stuffed animals, squishmallow collection, rare squishmallows, squishmallow database, kellytoy, squishy toys, collectible plushies',
    'og_image': 'https://squishmallowdex.com/og-image.png',  # You'll need to create this
    'site_name': 'Squishmallowdex',
    'twitter_handle': '@squishmallowdex',  # Change to your Twitter handle
}

SEO_META_TAGS = '''
<!-- SEO Meta Tags -->
<meta name="description" content="{description}"/>
<meta name="keywords" content="{keywords}"/>
<meta name="author" content="Squishmallowdex"/>
<meta name="robots" content="index, follow"/>
<link rel="canonical" href="{url}"/>

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website"/>
<meta property="og:url" content="{url}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{description}"/>
<meta property="og:image" content="{og_image}"/>
<meta property="og:site_name" content="{site_name}"/>

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:url" content="{url}"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{description}"/>
<meta name="twitter:image" content="{og_image}"/>
<meta name="twitter:site" content="{twitter_handle}"/>
<meta name="twitter:creator" content="{twitter_handle}"/>
'''

STRUCTURED_DATA = '''
<!-- Structured Data (JSON-LD) -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{site_name}",
  "description": "{description}",
  "url": "{url}",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": {{
      "@type": "EntryPoint",
      "urlTemplate": "{url}?q={{search_term_string}}"
    }},
    "query-input": "required name=search_term_string"
  }}
}}
</script>
'''


def inject_seo(html_content: str, config: dict) -> tuple[str, list[str]]:
    """
    Inject SEO meta tags and structured data into HTML.

    Args:
        html_content: The original HTML content
        config: Configuration dictionary with SEO values

    Returns:
        Tuple of (modified HTML, list of changes made)
    """
    changes = []
    modified_content = html_content

    # Check if SEO tags already exist
    has_description = 'name="description"' in html_content
    has_og_tags = 'property="og:title"' in html_content
    has_structured_data = 'application/ld+json' in html_content and 'WebSite' in html_content

    # Update or inject title tag
    title_pattern = r'<title>.*?</title>'
    if re.search(title_pattern, html_content, re.IGNORECASE):
        modified_content = re.sub(
            title_pattern,
            f'<title>{config["title"]}</title>',
            modified_content,
            count=1,
            flags=re.IGNORECASE
        )
        changes.append("Updated title tag")
    else:
        # If no title tag, we'll add it with the meta tags
        changes.append("Added title tag")

    # Prepare injections
    injections = []

    if not has_description or not has_og_tags:
        seo_tags = SEO_META_TAGS.format(**config)
        injections.append(seo_tags)
        changes.append("Added SEO meta tags and Open Graph tags")

    if not has_structured_data:
        structured_data = STRUCTURED_DATA.format(**config)
        injections.append(structured_data)
        changes.append("Added structured data (JSON-LD)")

    if not injections:
        return html_content, changes

    # Combine all injections
    combined_injection = '\n'.join(injections)

    # Find where to inject (after tracking scripts if they exist, or after <head>)
    # Look for the end of tracking scripts or just after <head>
    analytics_pattern = r'(gtag\(\'config\', \'G-[^\']+\'\);\s*</script>)'
    adsense_pattern = r'(pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^>]*>\s*</script>)'

    # Try to inject after AdSense (which should be last)
    if re.search(adsense_pattern, modified_content, re.DOTALL):
        modified_content = re.sub(
            adsense_pattern,
            r'\1\n' + combined_injection,
            modified_content,
            count=1,
            flags=re.DOTALL
        )
    # Try to inject after Analytics
    elif re.search(analytics_pattern, modified_content, re.DOTALL):
        modified_content = re.sub(
            analytics_pattern,
            r'\1\n' + combined_injection,
            modified_content,
            count=1,
            flags=re.DOTALL
        )
    # Otherwise inject right after <head>
    elif '<head>' in modified_content:
        modified_content = modified_content.replace(
            '<head>',
            f'<head>\n{combined_injection}',
            1
        )
    elif '<HEAD>' in modified_content:
        modified_content = modified_content.replace(
            '<HEAD>',
            f'<HEAD>\n{combined_injection}',
            1
        )
    else:
        print("  ❌ No <head> tag found")
        return html_content, []

    return modified_content, changes


def process_file(file_path: Path, config: dict) -> bool:
    """
    Process a single HTML file.

    Args:
        file_path: Path to the HTML file
        config: Configuration dictionary

    Returns:
        True if file was modified, False otherwise
    """
    print(f"Processing: {file_path}")

    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Inject SEO
        modified_content, changes = inject_seo(original_content, config)

        # Only write if content changed
        if modified_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"  ✅ Changes made:")
            for change in changes:
                print(f"     - {change}")
            return True
        else:
            print(f"  ⚠️  All SEO tags already present, skipping")
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
    config = DEFAULT_CONFIG.copy()

    # Parse command line arguments
    args = sys.argv[1:]
    target = None

    i = 0
    while i < len(args):
        if args[i] == '--url' and i + 1 < len(args):
            config['url'] = args[i + 1]
            config['og_image'] = f"{args[i + 1]}/og-image.png"
            i += 2
        elif args[i] == '--title' and i + 1 < len(args):
            config['title'] = args[i + 1]
            i += 2
        elif args[i] == '--description' and i + 1 < len(args):
            config['description'] = args[i + 1]
            i += 2
        else:
            target = Path(args[i])
            i += 1

    # Default target if not specified
    if target is None:
        target = Path("squishmallowdex.html")

    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"SEO Configuration:")
    print(f"  URL: {config['url']}")
    print(f"  Title: {config['title']}")
    print(f"  Description: {config['description'][:60]}...")
    print(f"{'='*60}\n")

    files_processed = 0
    files_modified = 0

    if target.is_file():
        # Process single file
        if target.suffix.lower() == '.html':
            files_processed = 1
            if process_file(target, config):
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
            if process_file(html_file, config):
                files_modified += 1

    print(f"\n{'='*60}")
    print(f"Summary: {files_modified}/{files_processed} files modified")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
