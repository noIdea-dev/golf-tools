# sources/api_client.py
import os
import time
import typing as t

import requests


class ApiClient:
    """
    Thin wrapper for golf course data APIs.

    You will need to:
    - Choose a specific provider (e.g., Zyla Golf Courses Data API, Golf API, Golf Course Database API).
    - Configure API base URL and key via environment variables or config.
    """

    def __init__(self, log_file: str, dry_run: bool = False):
        self.log_file = log_file
        self.dry_run = dry_run

        # TODO: adapt these names to the chosen API provider.
        self.base_url = os.environ.get("GOLF_API_BASE_URL", "").rstrip("/")
        self.api_key = os.environ.get("GOLF_API_KEY", "")
        self.rate_limit_delay = float(os.environ.get("GOLF_API_DELAY", "1.0"))

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
        Yield course dicts for the given ISO country code.

        Expected output per course:
        {
            "id": "...",
            "name": "Course Name",
            "country_code": "TH",
            "city": "Bangkok",
            "lat": 13.7,
            "lon": 100.5,
            "source": "api",
            "detail_url": "https://..."  # if the API has a public URL
        }
        """
        if not self.base_url or not self.api_key:
            self._log("[API] No base URL or API key configured; skipping API tier.")
            return []

        # TODO: Replace with the provider-specific endpoint and parameters.
        # Example: using a hypothetical /courses endpoint with country filter.
        page = 1
        page_size = 50

        while True:
            params = {
                "country": country_code,
                "page": page,
                "page_size": page_size,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            }
            url = f"{self.base_url}/courses"

            self._log(f"[API] GET {url} {params}")

            if self.dry_run:
                # Just pretend we saw zero courses
                return []

            resp = requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code != 200:
                self._log(f"[API] Non-200 response {resp.status_code}: {resp.text[:200]}")
                return []

            data = resp.json()
            courses = data.get("courses") or data.get("results") or []
            if not courses:
                break

            for c in courses:
                # Normalize fields based on provider
                course = {
                    "id": c.get("id") or c.get("course_id"),
                    "name": c.get("name") or c.get("course_name"),
                    "country_code": country_code,
                    "city": c.get("city"),
                    "lat": c.get("latitude") or c.get("lat"),
                    "lon": c.get("longitude") or c.get("lon"),
                    "source": "api",
                    "detail_url": c.get("url") or c.get("website"),
                    "raw": c,
                }
                yield course

            page += 1
            time.sleep(self.rate_limit_delay)

    def get_course_scorecard(self, course: dict) -> t.Optional[dict]:
        """
        Fetch structured scorecard data for a course if supported by the API.

        Expected output:
        {
            "tees": [
                {
                    "name": "Blue",
                    "gender": "M",
                    "rating": 72.1,
                    "slope": 135,
                    "holes": [
                        {"number": 1, "par": 4, "si": 7, "yards": 420},
                        ...
                    ]
                },
                ...
            ]
        }
        """
        if not self.base_url or not self.api_key:
            return None

        # TODO: use provider-specific endpoint (e.g., /courses/{id}/scorecard)
        course_id = course.get("id")
        if not course_id:
            return None

        url = f"{self.base_url}/courses/{course_id}/scorecard"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        self._log(f"[API] GET {url}")

        if self.dry_run:
            return None

        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            self._log(f"[API] Non-200 scorecard response {resp.status_code}: {resp.text[:200]}")
            return None

        data = resp.json()
        # You may want to adjust normalization based on actual API schema.
        return data
