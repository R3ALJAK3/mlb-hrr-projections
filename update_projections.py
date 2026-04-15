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
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # FIXED: Using just 'gemini-1.5-flash' without prefixes
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"Using this MLB slate: {slate_info}. Calculate HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team. Return ONLY a valid JSON object where keys are game names (e.g., 'NYY @ BOS') and values are lists of objects with 'name' and 'hrr' keys."

    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    # Clean potential markdown
    if "```" in raw_text:
        raw_text = raw_text.split("```")[1].replace("json", "").strip()
    
    json_data = json.loads(raw_text)
    
    with open("data.json", "w") as f:
        json.dump(json_data, f, indent=4)
    print("Successfully updated data.json")

except Exception as e:
    # This ensures something is always written so the site doesn't stay blank
    with open("data.json", "w") as f:
        json.dump({"error": str(e), "date": today}, f)
        
