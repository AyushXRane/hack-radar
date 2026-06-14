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
