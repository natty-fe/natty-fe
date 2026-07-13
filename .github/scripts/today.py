"""
Generates a live, neofetch-style stat card (ASCII portrait + GitHub stats)
as light_mode.svg and dark_mode.svg, embedded in README.md.

Requires an env var GH_TOKEN: a GitHub personal access token
(classic, scopes: read:user, repo) stored as a repo secret.
"""
import os
import sys
import datetime
import requests

sys.path.insert(0, os.path.dirname(__file__))
from ascii_art import image_to_ascii
from svg_card import render_card

USERNAME = os.environ.get("GH_USERNAME", "natty-fe")
TOKEN = os.environ.get("GH_TOKEN")
API_URL = "https://api.github.com/graphql"

HEADERS = {"Authorization": f"bearer {TOKEN}"}

USER_QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    login
    createdAt
    followers { totalCount }
    following { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        primaryLanguage { name }
      }
    }
  }
}
"""

CONTRIB_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
    }
  }
}
"""

def gql(query, variables):
    resp = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def fetch_stats():
    user_data = gql(USER_QUERY, {"login": USERNAME})["user"]
    created = datetime.datetime.fromisoformat(user_data["createdAt"].replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)

    total_commits = total_prs = total_issues = total_repo_contribs = 0
    year = created.year
    while year <= now.year:
        start = max(created, datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc))
        end = min(now, datetime.datetime(year, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc))
        c = gql(CONTRIB_QUERY, {
            "login": USERNAME,
            "from": start.isoformat(),
            "to": end.isoformat(),
        })["user"]["contributionsCollection"]
        total_commits += c["totalCommitContributions"]
        total_prs += c["totalPullRequestContributions"]
        total_issues += c["totalIssueContributions"]
        total_repo_contribs += c["totalRepositoryContributions"]
        year += 1

    repos = user_data["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    lang_bytes = {}
    for r in repos:
        lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else None
        if lang:
            lang_bytes[lang] = lang_bytes.get(lang, 0) + 1
    top_langs = sorted(lang_bytes, key=lang_bytes.get, reverse=True)[:5]

    uptime = now - created
    years = uptime.days // 365
    months = (uptime.days % 365) // 30

    return {
        "login": user_data["login"],
        "name": user_data["name"] or user_data["login"],
        "followers": user_data["followers"]["totalCount"],
        "following": user_data["following"]["totalCount"],
        "public_repos": user_data["repositories"]["totalCount"],
        "total_stars": total_stars,
        "total_commits": total_commits,
        "total_prs": total_prs,
        "total_issues": total_issues,
        "top_langs": top_langs,
        "account_years": years,
        "account_months": months,
    }

def build_stat_lines(s):
    return [
        f"{s['login']}@github" + " " * 6 + "-" * 20,
        f"Account Age: ......... {s['account_years']} years, {s['account_months']} months",
        f"Public Repos: ........ {s['public_repos']}",
        f"Followers: ........... {s['followers']}",
        f"Following: ........... {s['following']}",
        "",
        "--- Contributions ---",
        f"Total Commits: ....... {s['total_commits']}",
        f"Pull Requests: ....... {s['total_prs']}",
        f"Issues: .............. {s['total_issues']}",
        f"Total Stars Earned: .. {s['total_stars']}",
        "",
        "--- Top Languages ---",
        f"{', '.join(s['top_langs']) if s['top_langs'] else 'n/a'}",
    ]

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    photo_path = os.path.join(repo_root, "profile.jpg")

    if not TOKEN:
        print("GH_TOKEN not set — skipping live fetch, cannot generate card.", file=sys.stderr)
        sys.exit(1)

    stats = fetch_stats()
    stat_lines = build_stat_lines(stats)
    ascii_lines = image_to_ascii(photo_path, cols=64, crop_box=(140, 200, 920, 1300))

    for theme in ("dark", "light"):
        svg = render_card(ascii_lines, stat_lines, theme=theme, title=f"{stats['login']}@github")
        out_path = os.path.join(repo_root, f"{theme}_mode.svg")
        with open(out_path, "w") as f:
            f.write(svg)
        print(f"wrote {out_path}")

if __name__ == "__main__":
    main()
