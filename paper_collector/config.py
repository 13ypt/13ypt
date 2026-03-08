"""
Configuration for the Egypt Animal Cult Paper Collector.
古代エジプト動物崇拝 論文自動収集アプリ 設定ファイル
"""

# Search queries for academic APIs
# These are combined with OR logic when searching
SEARCH_QUERIES = [
    "ancient Egypt animal cult",
    "ancient Egypt animal worship",
    "Egyptian animal mummy",
    "Egyptian sacred animal",
    "Egyptian crocodile cult",
    "Egyptian ibis cult",
    "Egyptian falcon catacomb",
    "Ptolemaic Egypt animal",
    "Saqqara animal necropolis",
    "Egyptian zoological mummy",
    "ancient Egypt Sobek crocodile",
    "ancient Egypt Thoth ibis",
    "ancient Egypt Apis bull",
    "ancient Egypt Bastet cat",
    "Egyptian animal catacomb",
]

# OpenAlex API configuration (free, no API key required)
OPENALEX_BASE_URL = "https://api.openalex.org"
# Polite pool: set your email for faster rate limits
OPENALEX_EMAIL = ""  # e.g. "your-email@example.com"

# CrossRef API configuration (free, no API key required)
CROSSREF_BASE_URL = "https://api.crossref.org"
# Polite pool: set your email for faster rate limits
CROSSREF_EMAIL = ""  # e.g. "your-email@example.com"

# How many days back to search on each run
DEFAULT_DAYS_BACK = 7

# Database file to store collected papers
DB_FILE = "collected_papers.db"

# Output directory for reports
OUTPUT_DIR = "reports"

# Rate limiting (seconds between API requests)
REQUEST_DELAY = 1.0

# Maximum results per query per source
MAX_RESULTS_PER_QUERY = 50
