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

