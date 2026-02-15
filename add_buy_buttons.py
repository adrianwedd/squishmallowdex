#!/usr/bin/env python3
"""
Quick script to add buy buttons to existing squishmallowdex.html
without regenerating the entire collection.
"""

import re
import sys

def add_buy_buttons(html_path: str):
    """Add buy button column to existing HTML"""

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Check if buy buttons already exist
    if '🛒' in html or 'buy-btn' in html:
        print("✅ Buy buttons already present!")
        return

    print("Adding buy buttons to HTML...")

    # 1. Add column to header
    # Find: <th data-col="1" data-sortable="false" data-hidden="false">Own</th>
    # Add after: <th data-col="2" data-sortable="false" data-hidden="false">🛒</th>

    header_pattern = r'(<th data-col="1"[^>]*>Own</th>)'
    header_replacement = r'\1\n      <th data-col="2" data-sortable="false" data-hidden="false">🛒</th>'
    html = re.sub(header_pattern, header_replacement, html)

    # 2. Add buy button CSS
    css_insert = """
  /* Buy button */
  .buy-btn {
    display: inline-block;
    background: var(--accent);
    color: white;
    text-decoration: none;
    font-size: 18px;
    padding: 6px 12px;
    border-radius: 8px;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
  }
  .buy-btn:hover {
    transform: scale(1.1);
    background: #00a3b8;
    box-shadow: 0 2px 8px rgba(0, 188, 212, 0.3);
  }
  .buy-btn:active {
    transform: scale(0.95);
  }
"""

    # Insert before </style>
    html = html.replace('</style>', css_insert + '</style>')

    # 3. Add footer with FTC disclosure
    footer_html = """
<footer class="site-footer">
  <p class="ftc-disclosure">
    <strong>Affiliate Disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases.
    When you buy through our links, we may earn a small commission at no extra cost to you.
    This helps support this free educational project. Thank you! ❤️
  </p>
  <p class="footer-links">
    <a href="about.html">About</a> •
    <a href="guide.html">Usage Guide</a> •
    <a href="https://github.com/adrianwedd/squishmallowdex" target="_blank" rel="noopener">GitHub</a>
  </p>
</footer>
"""

    footer_css = """
  /* Footer */
  .site-footer {
    background: var(--ink);
    color: white;
    padding: 24px 20px;
    margin-top: 40px;
    text-align: center;
  }
  .ftc-disclosure {
    margin: 0 0 12px;
    font-size: 13px;
    opacity: 0.9;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
  }
  .ftc-disclosure strong {
    color: var(--accent);
  }
  .footer-links {
    margin: 0;
    font-size: 14px;
  }
  .footer-links a {
    color: var(--accent);
    text-decoration: none;
    margin: 0 8px;
  }
  .footer-links a:hover {
    text-decoration: underline;
  }
"""

    html = html.replace('</style>', footer_css + '</style>')
    html = html.replace('</body>', footer_html + '\n</body>')

    # 4. Add buy buttons to table rows
    # This is tricky - need to add a cell after each "Own" checkbox cell
    # Pattern: find each row, add buy button cell after Own cell

    # Extract all Squishmallow names and create buy buttons for each row
    # We'll use a simpler approach: add a column via JavaScript

    buy_button_script = """
  // Add buy button column dynamically
  (function() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 2) {
        // Get name from Name column (usually column 3)
        const nameCell = cells[3];
        const name = nameCell ? nameCell.textContent.trim() : '';

        // Create buy button cell
        const buyCell = document.createElement('td');
        buyCell.setAttribute('data-col', '2');

        if (name) {
          const searchQuery = encodeURIComponent(`${name} squishmallow`);
          const buyLink = document.createElement('a');
          buyLink.href = `https://www.amazon.com/s?k=${searchQuery}&tag=adrianwedd-20`;
          buyLink.target = '_blank';
          buyLink.rel = 'noopener';
          buyLink.className = 'buy-btn';
          buyLink.setAttribute('data-id', row.dataset.id);
          buyLink.setAttribute('aria-label', 'Buy on Amazon');
          buyLink.textContent = '🛒';
          buyCell.appendChild(buyLink);
        }

        // Insert after Own cell (index 1)
        cells[1].after(buyCell);
      }
    });

    // Update colConfig to include new column
    const colBtn = document.getElementById('colBtn');
    if (colBtn) {
      // Column picker already exists, add our column to it
      console.log('✅ Buy buttons added!');
    }
  })();
"""

    # Insert before closing </script>
    html = html.replace('})();\n</script>', '})();\n' + buy_button_script + '</script>')

    # Write back
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Buy buttons added to {html_path}")
    print("🛒 Affiliate ID: adrianwedd-20")

if __name__ == "__main__":
    html_file = "docs/squishmallowdex.html"
    add_buy_buttons(html_file)
