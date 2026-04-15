import os
import requests
import json
import google.generativeai as genai

# 1. Get EVERY MLB Game for Jackie Robinson Day
try:
    url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-04-15"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # We are taking ALL games from the list, no filters.
    games = data['dates'][0].get('games', []) if 'dates' in data and data['dates'] else []
    
    slate_info = "\n".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in games])
except Exception as e:
    slate_info = "April 15, 2026 MLB Slate"

# 2. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Prompt for the Full 15-Game Slate
prompt = f"""Using this COMPLETE MLB slate: {slate_info}, calculate HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team. 
Return ONLY a valid JSON object. Do not skip finished games. Do not include markdown formatting."""

# 4. Ask and Save
try:
    response = model.generate_content(prompt)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    
    with open("data.json", "w") as f:
        f.write(clean_json)
    print(f"Success: Processed all {len(games)} games for the full day slate.")
except Exception as e:
    print(f"Error: {e}")
    with open("data.json", "w") as f:
        f.write("{}")
