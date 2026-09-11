# sources/directory_scraper.py
import os
import time
import typing as t
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class DirectoryScraper:
    """
    Scrape public golf course directories by country and attempt to locate scorecard images/PDFs.

    You must configure:
    - BASE_DIRECTORY_URL_TEMPLATE
      e.g. for an AllSquare-like site: "https://www.example.com/directory/golf-courses/{country_slug}"
    - A mapping from ISO country code -> directory slug, e.g. "TH" -> "thailand".
    """

    def __init__(self, log_file: str, dry_run: bool = False):
        self.log_file = log_file
        self.dry_run = dry_run

        # TODO: configure this for a real directory (GolfSG, AllSquare, etc.).
        self.base_directory_template = os.environ.get(
            "GOLF_DIR_TEMPLATE", "https://example.com/directory/golf-courses/{country_slug}"
        )
        # Minimal mapping; extend as needed
        self.country_slug_map = {
            "TH": "thailand",
            "ID": "indonesia",
            "SG": "singapore",
            "MY": "malaysia",
            "PH": "philippines",
            "VN": "vietnam",
            "JP": "japan",
        }
        self.rate_limit_delay = float(os.environ.get("GOLF_DIR_DELAY", "1.0"))
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; GolfCourseScraper/1.0)",
                "Accept-Language": "en-US,en;q=0.8",
            }
        )

    def _log(self, msg: str):
        line = msg
        print(line)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def iter_courses_by_country(self, country_code: str) -> t.Iterable[dict]:
        """
        Yield course dicts discovered via directory listing for the given country.
        Expected fields:
        {
            "name": "Course Name",
            "country_code": "TH",
            "source": "directory",
            "detail_url": "https://example.com/course/...",
        }
        """
        slug = self.country_slug_map.get(country_code)
        if not slug:
            self._log(f"[DIR] No directory slug configured for {country_code}; skipping.")
            return []

        start_url = self.base_directory_template.format(country_slug=slug)
        self._log(f"[DIR] Fetching country directory: {start_url}")

        if self.dry_run:
            return []

        resp = self.session.get(start_url, timeout=30)
        if resp.status_code != 200:
            self._log(f"[DIR] Non-200 country directory response {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # TODO: adjust selectors based on the specific directory HTML.
        # Example: list items containing course cards with links.
        course_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = (a.get_text() or "").strip()
            if not text:
                continue
            # Very rough heuristic; tighten to match actual site structure.
            if "course" in href.lower() and "golf" in text.lower():
                course_links.append((text, urljoin(start_url, href)))

        seen_urls = set()
        for name, url in course_links:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            yield {
                "name": name,
                "country_code": country_code,
                "source": "directory",
                "detail_url": url,
            }

    def download_scorecard_for_course(self, course: dict, local_dir: str) -> t.Optional[dict]:
        """
        For a given course discovered by the directory, attempt to find and download a scorecard.

        Strategy:
        - Load the course detail page.
        - Look for <img> tags with 'scorecard' in src/alt/title.
        - Look for <a> tags to PDFs with 'scorecard' in href.
        - Download the first plausible match to local_dir.
        """
        url = course.get("detail_url")
        if not url:
            self._log("[DIR] No detail_url for course; cannot scrape.")
            return None

        self._log(f"[DIR] Fetching course page: {url}")

        if self.dry_run:
            return None

        resp = self.session.get(url, timeout=30)
        if resp.status_code != 200:
            self._log(f"[DIR] Non-200 course page response {resp.status_code} for {url}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # 1. Look for images with scorecard in attributes
        candidates = []

        for img in soup.find_all("img"):
            src = img.get("src") or ""
            alt = (img.get("alt") or "").lower()
            title = (img.get("title") or "").lower()
            if "scorecard" in src.lower() or "scorecard" in alt or "scorecard" in title:
                candidates.append(urljoin(url, src))

        # 2. Look for PDF links with scorecard in href or link text
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = (a.get_text() or "").lower()
            if "scorecard" in href.lower() or "scorecard" in text:
                if href.lower().endswith(".pdf"):
                    candidates.append(urljoin(url, href))

        if not candidates:
            self._log(f"[DIR] No obvious scorecard assets found for {course['name']}")
            return None

        asset_url = candidates[0]
        filename = os.path.basename(asset_url.split("?")[0]) or "scorecard"

        # Ensure extension
        if not any(filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".pdf"]):
            # Default to .png if unknown
            filename = filename + ".png"

        local_path = os.path.join(local_dir, filename)

        self._log(f"[DIR] Downloading scorecard asset: {asset_url} -> {local_path}")

        asset_resp = self.session.get(asset_url, timeout=30)
        if asset_resp.status_code != 200:
            self._log(f"[DIR] Non-200 asset response {asset_resp.status_code} for {asset_url}")
            return None

        with open(local_path, "wb") as f:
            f.write(asset_resp.content)

        time.sleep(self.rate_limit_delay)

        return {
            "url": asset_url,
            "file": filename,
        }
