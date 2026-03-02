"""
Affiliate Configuration for Squishmallowdex

Set your Amazon Associates affiliate ID here once you're approved.
"""

from urllib.parse import quote_plus

# Amazon Associates Configuration
# Get your ID from: https://affiliate-program.amazon.com/
AMAZON_ASSOCIATE_ID = "adrianwedd-20"  # ✅ Real Amazon Associates ID

# Amazon base URLs by marketplace
AMAZON_URL_BASE = {
    "US": "https://www.amazon.com",
    "UK": "https://www.amazon.co.uk",
    "CA": "https://www.amazon.ca",
    "DE": "https://www.amazon.de",
    "FR": "https://www.amazon.fr",
    "ES": "https://www.amazon.es",
    "IT": "https://www.amazon.it",
    "JP": "https://www.amazon.co.jp",
}

# Default marketplace
DEFAULT_MARKETPLACE = "US"


def generate_affiliate_link(asin: str, marketplace: str = DEFAULT_MARKETPLACE) -> str:
    """
    Generate an Amazon affiliate link from an ASIN.

    Args:
        asin: Amazon Standard Identification Number
        marketplace: Amazon marketplace (US, UK, CA, etc.)

    Returns:
        Full affiliate URL with tracking tag
    """
    base_url = AMAZON_URL_BASE.get(marketplace, AMAZON_URL_BASE["US"])
    return f"{base_url}/dp/{asin}?tag={AMAZON_ASSOCIATE_ID}"


def search_amazon_url(name: str, marketplace: str = DEFAULT_MARKETPLACE) -> str:
    """
    Generate an Amazon search URL for a Squishmallow by name.

    Args:
        name: Squishmallow name
        marketplace: Amazon marketplace

    Returns:
        Amazon search URL with affiliate tag
    """
    base_url = AMAZON_URL_BASE.get(marketplace, AMAZON_URL_BASE["US"])
    query = quote_plus(f"{name} squishmallow")
    return f"{base_url}/s?k={query}&tag={AMAZON_ASSOCIATE_ID}"
