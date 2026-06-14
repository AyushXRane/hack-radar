#!/usr/bin/env python3
"""
radar.py - hack-radar core script
 
Usage:
    python radar.py velocity
    python radar.py api-check
    python radar.py pivot
    python radar.py competitors
    python radar.py rubric
    python radar.py submission
    python radar.py report
 
Reads hackathon.config.json from the current directory.
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
 
import requests
from bs4 import BeautifulSoup
 
CONFIG_PATH = Path("hackathon.config.json")

def load_config():
    if not CONFIG_PATH.exists():
        print("No hackathon.config.json found in the current directory. Run setup first.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)
 
 
def run_git(args, repo_path):
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True, text=True
    )
    return result.stdout.strip()
 
 
## velocity
 
def cmd_velocity(config):
    repo = config["repo_path"]
 
    last_hour = run_git(["log", "--oneline", "--since=1 hour ago"], repo)
    commits_last_hour = len([l for l in last_hour.splitlines() if l])
 
    last_3h = run_git(["log", "--oneline", "--since=3 hours ago"], repo)
    commits_last_3h = len([l for l in last_3h.splitlines() if l])
 
    end_time = datetime.fromisoformat(config["hackathon_end_time"])
    now = datetime.now(end_time.tzinfo) if end_time.tzinfo else datetime.now()
    hours_left = max((end_time - now).total_seconds() / 3600, 0)
 
    rate_per_hour = commits_last_3h / 3
    projected = rate_per_hour * hours_left
 
    if commits_last_hour == 0:
        status = "inactive"
    elif commits_last_hour <= 2:
        status = "low activity"
    else:
        status = "good pace"
 
    print(f"Commits last hour: {commits_last_hour} ({status})")
    print(f"Commits last 3 hours: {commits_last_3h}")
    print(f"Hours remaining: {hours_left:.1f}")
    print(f"Projected commits in remaining time at current pace: {projected:.1f}")
    if rate_per_hour == 0 and hours_left > 0:
        print("No recent commits with time still remaining. The team may be stuck.")
 
 
## api_check
 
def cmd_api_check(config):
    repo = config["repo_path"]
    apis = config.get("sponsor_apis", [])
 
    if not apis:
        print("No sponsor APIs listed in config.")
        return
 
    for api in apis:
        keyword = re.sub(r"\s+", "", api.lower())
        result = subprocess.run(
            ["grep", "-ri", keyword, "-r", repo,
             "--include=*.py", "--include=*.js", "--include=*.ts"],
            capture_output=True, text=True
        )
        lines = [l for l in result.stdout.splitlines() if l]
 
        if not lines:
            print(f"{api}: not found in codebase")
            continue
 
        import_lines = [l for l in lines if re.search(r"\b(import|require|from)\b", l)]
        call_lines = [l for l in lines if l not in import_lines]
 
        if call_lines:
            print(f"{api}: actively used ({len(call_lines)} call site(s))")
        else:
            print(f"{api}: imported but no calls found")
 
 
## pivot
 
def cmd_pivot(config):
    repo = config["repo_path"]
    commits = run_git(["log", "--oneline", "-10"], repo)
 
    print(f"Original project idea: {config['project_idea']}")
    print("Last 10 commits:")
    print(commits if commits else "(no commits found)")
    print()
    print("Compare the commits above to the original idea. If recent work "
          "suggests a different direction, flag it to the user and ask if "
          "they want to update the config.")
 
 
## competitors
 
def cmd_competitors(config):
    devpost_url = config["devpost_url"].rstrip("/")
    gallery_url = f"{devpost_url}/project-gallery"
 
    try:
        resp = requests.get(gallery_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Could not fetch project gallery ({gallery_url}): {e}")
        return
 
    soup = BeautifulSoup(resp.text, "html.parser")
    entries = soup.select("div.gallery-item, div.software-entry, div.entry-grid div")
 
    if not entries:
        print("No project entries found. The gallery page structure may have "
              f"changed. Check manually: {gallery_url}")
        return
 
    idea_words = set(re.findall(r"[a-z]+", config["project_idea"].lower()))
 
    print(f"Project idea: {config['project_idea']}")
    print(f"Prize tracks: {', '.join(config.get('prize_tracks', []))}")
    print(f"Found {len(entries)} entries in the gallery:\n")
 
    for entry in entries[:40]:
        title_el = entry.select_one("h5, h4, .software-name, a")
        desc_el = entry.select_one("p, .tagline")
        title = title_el.get_text(strip=True) if title_el else "Unknown"
        desc = desc_el.get_text(strip=True) if desc_el else ""
 
        desc_words = set(re.findall(r"[a-z]+", desc.lower()))
        overlap = idea_words & desc_words
 
        flag = " <- possible overlap" if len(overlap) >= 3 else ""
        print(f"- {title}: {desc}{flag}")
 
    print("\nFor each flagged entry, check whether it's likely targeting the "
          "same sponsor or prize track as this project. If so, identify what "
          "this project does differently or better, and note any gaps in the "
          "other project that this one could exploit.")
 
 
## rubric 
 
def cmd_rubric(config):
    devpost_url = config["devpost_url"].rstrip("/")
    rules_url = f"{devpost_url}/rules"
 
    try:
        resp = requests.get(rules_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Could not fetch rules page ({rules_url}): {e}")
        return
 
    soup = BeautifulSoup(resp.text, "html.parser")
 
    header = soup.find(
        lambda tag: tag.name in ("h2", "h3", "h4")
        and "judging criteria" in tag.get_text(strip=True).lower()
    )
 
    if not header:
        print(f"Could not find a 'Judging Criteria' section. Check manually: {rules_url}")
        return
 
    criteria = []
    for sibling in header.find_all_next():
        if sibling.name in ("h2", "h3", "h4"):
            break
        if sibling.name in ("li", "p"):
            text = sibling.get_text(strip=True)
            if text:
                criteria.append(text)
 
    print(f"Project idea: {config['project_idea']}\n")
    print("Judging criteria:")
    for c in criteria:
        print(f"- {c}")
 
    print("\nScore the project idea against each criterion from 1-10. "
          "Flag any criterion scoring below 6 and suggest how to address it.")
 
 
## submission
 
def cmd_submission(config):
    submission_url = config.get("submission_url")
    if not submission_url:
        print("No submission_url set in hackathon.config.json yet.")
        return
 
    try:
        resp = requests.get(submission_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Could not fetch submission page ({submission_url}): {e}")
        return
 
    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text(" ", strip=True).lower()
 
    checks = {
        "description filled out": "inspiration" in page_text or "what it does" in page_text,
        "tech stack listed": "built with" in page_text,
        "how it was built": "how i built it" in page_text or "how we built it" in page_text,
        "challenges section": "challenges i ran into" in page_text or "challenges we ran into" in page_text,
        "not still a draft": "this is a draft" not in page_text,
    }
 
    for label, passed in checks.items():
        print(f"{label}: {'OK' if passed else 'MISSING'}")
 
    for api in config.get("sponsor_apis", []):
        mentioned = api.lower() in page_text
        print(f"{api} mentioned: {'yes' if mentioned else 'no'}")
 
 
## demo-prep
 
CODE_EXTENSIONS = (
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java",
    ".rb", ".swift", ".c", ".cpp", ".html", ".css",
)
 
 
def cmd_demo_prep(config):
    repo = Path(config["repo_path"])
 
    readme = None
    for name in ("README.md", "readme.md", "Readme.md", "README.MD"):
        candidate = repo / name
        if candidate.exists():
            readme = candidate
            break
 
    if readme:
        content = readme.read_text(errors="ignore")
        print("README content:")
        print(content[:4000])
    else:
        print("No README found in the repo.")
 
    print("\nProject files:")
    tracked = run_git(["ls-files"], str(repo))
    files = [f for f in tracked.splitlines() if f]
    print("\n".join(files[:100]))
 
    print("\nRecent commits:")
    print(run_git(["log", "--oneline", "-20"], str(repo)))
 
    changed = run_git(["log", "--name-only", "--pretty=format:", "-10"], str(repo))
    changed_files = sorted(set(f for f in changed.splitlines() if f.strip()))
    code_files = [f for f in changed_files if f.endswith(CODE_EXTENSIONS)]
 
    print(f"\nRecently changed source files ({len(code_files)}):")
    for f in code_files[:8]:
        full_path = repo / f
        if not full_path.is_file():
            continue
        try:
            content = full_path.read_text(errors="ignore")
        except OSError:
            continue
        print(f"\n--- {f} ---")
        print(content[:3000])
 
    print("\nUsing the README, project file list, recently changed source "
          "files, and commit history above, draft a 60-90 second demo "
          "script: what to show on screen, in what order, and what to say "
          "at each step. Base this on what the code actually does, not just "
          "the commit messages. Then draft a short slide outline covering "
          "the problem, the solution, a live demo placeholder, the tech "
          "stack, and the impact or what's next.")
 
 
## report
 
def cmd_report(config):
    sections = [
        ("Velocity", cmd_velocity),
        ("API usage", cmd_api_check),
        ("Pivot check", cmd_pivot),
        ("Competitors", cmd_competitors),
        ("Rubric", cmd_rubric),
    ]
    for title, fn in sections:
        print(f"=== {title} ===")
        fn(config)
        print()
 
 COMMANDS = {
    "velocity": cmd_velocity,
    "api-check": cmd_api_check,
    "pivot": cmd_pivot,
    "competitors": cmd_competitors,
    "rubric": cmd_rubric,
    "submission": cmd_submission,
    "demo-prep": cmd_demo_prep,
    "report": cmd_report,
}
 
 
def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python radar.py [{'|'.join(COMMANDS.keys())}]")
        sys.exit(1)
 
    config = load_config()
    COMMANDS[sys.argv[1]](config)
 
 
if __name__ == "__main__":
    main()
