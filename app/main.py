import os
import time
from typing import List, Set

import requests
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SUBREDDITS = [s.strip() for s in os.getenv("SUBREDDITS", "").split(",") if s.strip()]
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"


def get_oauth_token() -> str:
    """
    Placeholder OAuth token request using client credentials.

    Depending on the exact Reddit approval/auth flow you are granted,
    you may need to adjust scopes and auth behavior.
    """
    response = requests.post(
        TOKEN_URL,
        auth=(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": REDDIT_USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": REDDIT_USER_AGENT,
    }


def fetch_new_posts(token: str, subreddit: str) -> list[dict]:
    url = f"{API_BASE}/r/{subreddit}/new"
    response = requests.get(
        url,
        headers=get_headers(token),
        params={"limit": 10},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    posts = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        posts.append(
            {
                "id": post.get("id", ""),
                "title": post.get("title", ""),
                "subreddit": post.get("subreddit", subreddit),
                "permalink": f"https://reddit.com{post.get('permalink', '')}",
            }
        )
    return posts


def matches_keywords(title: str, keywords: List[str]) -> List[str]:
    title_lower = title.lower()
    return [kw for kw in keywords if kw in title_lower]


def send_discord_alert(post: dict, matched_keywords: List[str]) -> None:
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL not set; skipping alert")
        return

    content = (
        "Keyword match found\n"
        f"Subreddit: r/{post['subreddit']}\n"
        f"Matched: {', '.join(matched_keywords)}\n"
        f"Link: {post['permalink']}"
    )

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": content},
        timeout=30,
    )
    response.raise_for_status()


def run() -> None:
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        raise RuntimeError("Missing Reddit OAuth environment variables")

    if not SUBREDDITS:
        raise RuntimeError("No subreddits configured")

    if not KEYWORDS:
        raise RuntimeError("No keywords configured")

    seen_post_ids: Set[str] = set()

    token = get_oauth_token()

    while True:
        try:
            for subreddit in SUBREDDITS:
                posts = fetch_new_posts(token, subreddit)
                for post in posts:
                    if post["id"] in seen_post_ids:
                        continue

                    matched = matches_keywords(post["title"], KEYWORDS)
                    if matched:
                        send_discord_alert(post, matched)

                    seen_post_ids.add(post["id"])

            time.sleep(POLL_SECONDS)

        except requests.HTTPError as exc:
            print(f"HTTP error: {exc}")
            time.sleep(POLL_SECONDS)
        except Exception as exc:
            print(f"Unexpected error: {exc}")
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
