"""General-purpose, polite web scraping helper.

Uses requests + BeautifulSoup to fetch a page and extract clean, readable text.
Keep scraping ethical:
- Always check a site's Terms of Service and robots.txt before scraping.
- Prefer official APIs (see nutrition.py) when they exist.
- Don't hammer servers; this helper fetches one page at a time.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib import robotparser

HEADERS = {"User-Agent": "FitnessNutritionChatbot/1.0 (educational project)"}


def _allowed_by_robots(url: str) -> bool:
    """Respect robots.txt. Returns True if scraping the URL is permitted."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        # If robots.txt can't be read, err on the side of allowing a single fetch.
        return True


def scrape_text(url: str, max_chars: int = 4000) -> str:
    """Fetch a URL and return its main visible text (trimmed to max_chars)."""
    if not url.startswith(("http://", "https://")):
        return "Please provide a full URL starting with http:// or https://"

    if not _allowed_by_robots(url):
        return f"robots.txt disallows scraping {url}. Skipping out of respect for the site."

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Could not fetch the page: {exc}"

    soup = BeautifulSoup(resp.text, "html.parser")

    # Drop noise.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:max_chars] if text else "No readable text found on that page."


if __name__ == "__main__":
    # Quick manual test: python scraper.py
    print(scrape_text("https://example.com"))
