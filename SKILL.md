---
Name: hack-radar
Description: Monitors a hackathon project's progress in real time. Checks git commits history, sponsor API usage, whether the team has pivoted from its original idea, competing Devpost projects in the same prize track, alignment with judging criteria, and submission readiness in the final two hours. Also drafts a demo script and slide outline from the repo's README, commit history and codebase. Use when a user wants a status check on their hackathon project, asks how they're doing, wants to know about competitors, wants help prepping their demo or pitch, or wants to verify their Devpost submission before the deadline.
---

hack-radar  
All checks run through scripts/radar.py, which reads hackathon.config.json from the project root.
Requires requests and beautifulsoup4. Install with pip install requests beautifulsoup4 if not already available. 

setup  
If hackathon.config.json does not exist, ask the user for:

project_idea: one sentence description  
tech_stack: list of technologies
repo_path: path to the local git repo
devpost_url: hackathon's Devpost URL
submission_url: the team's own Devpost submission URL (can be added later)
prize_tracks: list of tracks they're targeting
sponsor_apis: list of sponsor APIs being used
hackathon_end_time: ISO 8601 timestamp

Confirm with the user, then save as JSON.

commands  
```bash
python scripts/radar.py velocity
python scripts/radar.py api-check
python scripts/radar.py pivot
python scripts/radar.py competitors
python scripts/radar.py rubric
python scripts/radar.py submission
python scripts/radar.py demo-prep
python scripts/radar.py report
```
report runs velocity, api-check, pivot, competitors, and rubric together.  
velocity: commit counts for the last hour and last 3 hours, plus a pace projection against hackathon_end_time.
api-check: for each sponsor API in the config, reports whether it is unused, imported only, or actively called.
pivot: prints the original project idea and the last 10 commit messages. Compare them and tell the user if recent work has drifted from the original idea.
competitors: scrapes the Devpost project gallery and flags entries with significant word overlap with the project idea. For flagged entries, check whether they're likely targeting the same sponsor or prize track, and identify what this project does differently or better.
rubric: scrapes the judging criteria from the hackathon's rules page. Score the project idea against each criterion from 1-10 and flag anything below 6, with a suggestion for how to address it.
submission: only run when hackathon_end_time is within two hours. Checks the team's Devpost submission for a filled-out description, tech stack, "how it was built," challenges, and sponsor API mentions.
demo-prep: reads the repo's README, file structure, recently changed source files, and commit history, then drafts a short demo script (what to show, in what order, what to say) and a slide outline (problem, solution, demo, tech stack, impact). Base the script on what the code actually does, not just the commit messages.
