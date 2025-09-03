"""
Configuration file for YGG Torrent Parser
"""

# YGG Torrent base URL
BASE_URL = "https://www.yggtorrent.top"

# Your passkey (replace with your actual passkey)
PASSKEY = "DJdLXYBi2WmyQB0PdNWZ8u9RZEnTqiXT"

# Available subcategories
SUBCATEGORIES = {
    'Nintendo Games': 2163,
    'PlayStation Games': 2145,
    'Xbox Games': 2146,
    'PC Games': 2142,
    'Movies': 2188,
    'TV Shows': 2189,
    'Music': 2190,
    'Software': 2144,
    'Books': 2191,
    'Anime': 2192,
    'Documentaries': 2193,
    'Sports': 2194,
    'E-books': 2195,
    'Comics': 2196,
    'Mobile Games': 2197,
    'Retro Games': 2198
}

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# Output settings
DEFAULT_OUTPUT_DIR = "downloads"
JSON_OUTPUT_DIR = "data"
