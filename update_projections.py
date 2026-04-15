import os
import requests
import json
import google.generativeai as genai
from datetime import datetime

# 1. Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# 2. Get MLB Data
try:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    games = data['dates'][0].get('games', []) if 'dates' in data and data['dates'] else []
    slate_info = ", ".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in games])
except Exception as e:
    slate_info = "MLB Games"

# 3. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Generate Projections
# We use a simple string join here to avoid "Invalid format specifier" errors
prompt = "Using this MLB slate: " + slate_info + """. 
Calculate HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team. 
Return ONLY a valid JSON object where keys are game names (e.g., 'NYY @ BOS') and values are lists of objects with 'name' and 'hrr' keys. 
Do not include markdown or extra text."""

try:
    response = model.generate_content(prompt)
    # This logic strips out any ```json tags if Gemini includes them
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    
    # Validate it is real JSON before saving
    json_data = json.loads(raw_text.strip())
    
    with open("data.json", "w") as f:
        json.dump(json_data, f, indent=4)
    print("Successfully updated data.json")
except Exception as e:
    print(f"Error: {e}")
    # If it fails, don't write an empty file; keep the old one or show error
