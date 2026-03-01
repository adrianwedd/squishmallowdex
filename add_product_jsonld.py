#!/usr/bin/env python3
"""
Add enhanced JSON-LD structured data to squishmallowdex.py
This adds Product schema for each Squishmallow for better SEO.
"""

import sys
from pathlib import Path


def add_product_jsonld_to_template():
    """Add Product JSON-LD generation to the HTML template."""

    script_path = Path("squishmallowdex.py")

    if not script_path.exists():
        print("❌ Error: squishmallowdex.py not found")
        sys.exit(1)

    # Read the file
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already added
    if 'generate_product_jsonld' in content:
        print("⚠️  Product JSON-LD already exists in squishmallowdex.py")
        return False

    # Find the location to add the function (before render_html)
    insertion_point = content.find('def render_html(')

    if insertion_point == -1:
        print("❌ Error: Could not find render_html function")
        sys.exit(1)

    # Function to generate Product JSON-LD
    product_jsonld_function = '''
def generate_product_jsonld(name: str, description: str, image_url: str, wiki_url: str) -> str:
    """Generate Product schema JSON-LD for a Squishmallow."""
    import json

    # Clean up description
    desc = description.strip() if description else f"{name} Squishmallow plush toy"
    if len(desc) > 200:
        desc = desc[:197] + "..."

    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{name} Squishmallow",
        "description": desc,
        "image": image_url,
        "brand": {
            "@type": "Brand",
            "name": "Squishmallows"
        },
        "manufacturer": {
            "@type": "Organization",
            "name": "Kelly Toy Holdings LLC"
        },
        "url": wiki_url,
        "category": "Plush Toys",
        "offers": {
            "@type": "AggregateOffer",
            "availability": "https://schema.org/InStock",
            "priceCurrency": "USD",
            "lowPrice": "5.00",
            "highPrice": "100.00",
            "offerCount": "1"
        }
    }

    return json.dumps(product_schema, indent=2)


'''

    # Insert the function before render_html
    content = content[:insertion_point] + product_jsonld_function + content[insertion_point:]

    # Now find where to add the JSON-LD to each table row
    # Look for the table body generation
    body_function_start = content.find('def _build_table_body(')
    if body_function_start == -1:
        print("❌ Error: Could not find _build_table_body function")
        sys.exit(1)

    # Find the end of the function
    next_def = content.find('\ndef ', body_function_start + 1)
    body_function = content[body_function_start:next_def]

    # Check if we need to add JSON-LD to row data
    if 'data-jsonld' not in body_function:
        # Add instruction comment for manual implementation
        comment = '''
        # TODO: To add Product JSON-LD for each Squishmallow:
        # 1. Generate JSON-LD in _build_table_body for each row
        # 2. Add data-jsonld attribute to each <tr>
        # 3. Use JavaScript to inject into <head> when row is visible
        # Or generate a comprehensive ItemList JSON-LD in render_html
'''
        content = content[:next_def] + comment + content[next_def:]

    # Write back
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Added Product JSON-LD function to squishmallowdex.py")
    print("📝 Manual step required: Integrate JSON-LD into table rows or use ItemList")
    return True


def create_itemlist_jsonld_template():
    """Create a template for ItemList JSON-LD encompassing all Squishmallows."""

    template = '''
<!-- Comprehensive Collection JSON-LD -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Complete Squishmallows Collection",
  "description": "Browse and search through the complete collection of Squishmallows plush toys",
  "numberOfItems": "{total_count}",
  "itemListElement": [
    {item_list_elements}
  ]
}
</script>

<!-- Organization JSON-LD -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Squishmallowdex",
  "url": "https://squishmallowdex.com",
  "logo": "https://squishmallowdex.com/og-image.png",
  "description": "Your comprehensive Pokédex for Squishmallows - search, track, and collect",
  "sameAs": [
    "https://twitter.com/squishmallowdex",
    "https://github.com/adrianwedd/squishmallowdex"
  ]
}
</script>

<!-- BreadcrumbList JSON-LD -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://squishmallowdex.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Collection",
      "item": "https://squishmallowdex.com/squishmallowdex"
    }
  ]
}
</script>
'''

    with open('jsonld_template.html', 'w') as f:
        f.write(template)

    print("✅ Created jsonld_template.html")
    print("   Use this template to add comprehensive structured data")


if __name__ == '__main__':
    print("🔧 Adding Enhanced JSON-LD Structured Data\n")

    # Add function to squishmallowdex.py
    add_product_jsonld_to_template()

    # Create template
    create_itemlist_jsonld_template()

    print("\n" + "="*60)
    print("Next Steps:")
    print("1. Review the added function in squishmallowdex.py")
    print("2. Implement ItemList JSON-LD in render_html()")
    print("3. Test with Google Rich Results Test:")
    print("   https://search.google.com/test/rich-results")
    print("="*60)
