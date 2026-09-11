#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime

from sources.api_client import ApiClient
from sources.directory_scraper import DirectoryScraper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COURSES_DIR = os.path.join(BASE_DIR, "courses")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

ASIA_ISO_CODES = {
    "ID": "Indonesia",
    "TH": "Thailand",
    "SG": "Singapore",
    "MY": "Malaysia",
    "PH": "Philippines",
    "VN": "Viet Nam",
    "JP": "Japan",
    "KR": "Korea, Republic of",
    "CN": "China",
    "IN": "India",
    "LK": "Sri Lanka",
    "MM": "Myanmar",
    "KH": "Cambodia",
    "LA": "Lao People's Democratic Republic",
    "BD": "Bangladesh",
    "PK": "Pakistan",
    "AE": "United Arab Emirates",
    "QA": "Qatar",
    "SA": "Saudi Arabia",
    "OM": "Oman",
    "KW": "Kuwait",
    "BH": "Bahrain",
    "JO": "Jordan",
    "LB": "Lebanon",
    "TR": "Turkey",
    # Extend as needed
}


def ensure_dirs():
    os.makedirs(COURSES_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


def log_path(country_code: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return os.path.join(LOGS_DIR, f"run_{country_code}_{ts}.log")


def append_log(log_file: str, message: str):
    line = f"{datetime.utcnow().isoformat()}Z {message}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Golf course scorecard collector for Asian countries."
    )
    parser.add_argument(
        "--country",
        required=True,
        help="ISO 3166-1 alpha-2 country code (e.g. TH, ID, JP). Must be in Asia.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of courses to process (for testing).",
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Use API sources only, skip HTML/directory scraping.",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Skip API sources and use only directory scraping.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-download even if a course directory already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write any files; just log planned actions.",
    )
    return parser.parse_args()


def load_index(country_code: str):
    idx_path = os.path.join(COURSES_DIR, f"index_{country_code}.json")
    if not os.path.exists(idx_path):
        return {}
    with open(idx_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(country_code: str, index: dict):
    idx_path = os.path.join(COURSES_DIR, f"index_{country_code}.json")
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def course_dir(country_code: str, slug: str) -> str:
    return os.path.join(COURSES_DIR, country_code, slug)


def slugify(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace("'", "")
        .replace('"', "")
    )


def main():
    ensure_dirs()
    args = parse_args()
    country_code = args.country.upper()

    if country_code not in ASIA_ISO_CODES:
        print(f"Country {country_code} not recognised as Asia or not configured.")
        print(f"Configured: {', '.join(sorted(ASIA_ISO_CODES.keys()))}")
        sys.exit(1)

    log_file = log_path(country_code)
    append_log(log_file, f"Starting run for {country_code} ({ASIA_ISO_CODES[country_code]})")

    # Load / init index
    index = load_index(country_code)

    api_client = ApiClient(log_file=log_file, dry_run=args.dry_run)
    directory_scraper = DirectoryScraper(log_file=log_file, dry_run=args.dry_run)

    processed = 0

    # Tier 1: API
    if not args.no_api:
        append_log(log_file, "Tier 1: API sources enabled.")
        try:
            for course in api_client.iter_courses_by_country(country_code):
                if args.limit and processed >= args.limit:
                    break

                slug = slugify(course["name"])
                cdir = course_dir(country_code, slug)

                if os.path.exists(cdir) and not args.overwrite:
                    append_log(log_file, f"[API] Skipping existing course: {course['name']}")
                    continue

                append_log(log_file, f"[API] Processing course: {course['name']}")
                if not args.dry_run:
                    os.makedirs(cdir, exist_ok=True)

                # Fetch scorecard
                scorecard = api_client.get_course_scorecard(course)
                metadata = {
                    "course": course,
                    "scorecard_source": "api",
                    "country_code": country_code,
                    "local_dir": cdir,
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                }

                if not args.dry_run:
                    # Save metadata and raw structured scorecard
                    with open(os.path.join(cdir, "metadata.json"), "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)

                    if scorecard is not None:
                        with open(os.path.join(cdir, "scorecard.json"), "w", encoding="utf-8") as f:
                            json.dump(scorecard, f, indent=2, ensure_ascii=False)
                        # TODO: optional rendering to PNG from structured data
                    else:
                        append_log(log_file, f"[API] No scorecard data for {course['name']}")

                index[slug] = {
                    "name": course["name"],
                    "source": course.get("source", "api"),
                    "country_code": country_code,
                    "local_dir": cdir,
                }

                processed += 1
        except Exception as e:
            append_log(log_file, f"[API] Error during API tier: {e}")

    # Tier 2: Directories
    if not args.api_only:
        append_log(log_file, "Tier 2: Directory scraping enabled.")
        try:
            for course in directory_scraper.iter_courses_by_country(country_code):
                if args.limit and processed >= args.limit:
                    break

                slug = slugify(course["name"])
                cdir = course_dir(country_code, slug)

                if os.path.exists(cdir) and not args.overwrite:
                    append_log(log_file, f"[DIR] Skipping existing course: {course['name']}")
                    continue

                append_log(log_file, f"[DIR] Processing course: {course['name']}")
                if not args.dry_run:
                    os.makedirs(cdir, exist_ok=True)

                scorecard_result = directory_scraper.download_scorecard_for_course(course, cdir)

                metadata = {
                    "course": course,
                    "scorecard_source": "directory",
                    "country_code": country_code,
                    "local_dir": cdir,
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                }
                if scorecard_result:
                    metadata["scorecard_file"] = scorecard_result.get("file")
                    metadata["scorecard_url"] = scorecard_result.get("url")

                if not args.dry_run:
                    with open(os.path.join(cdir, "metadata.json"), "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)

                index[slug] = {
                    "name": course["name"],
                    "source": course.get("source", "directory"),
                    "country_code": country_code,
                    "local_dir": cdir,
                }

                processed += 1
        except Exception as e:
            append_log(log_file, f"[DIR] Error during directory tier: {e}")

    if not args.dry_run:
        save_index(country_code, index)

    append_log(log_file, f"Run complete. Processed {processed} courses for {country_code}.")


if __name__ == "__main__":
    main()
