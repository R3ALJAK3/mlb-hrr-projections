import os
import requests
import json
import google.generativeai as genai

# 1. Get COMPLETE MLB Data
try:
    url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-04-15"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    games = data['dates'][0].get('games', []) if 'dates' in data and data['dates'] else []
    
    # Filter for games that haven't finished
    active_games = [g for g in games if g.get('status', {}).get('abstractGameState') != 'Final']
    
    slate_info = "\n".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in active_games])
except Exception as e:
    slate_info = "April 15, 2026 MLB Slate"

# 2. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. New 'Aggressive' Prompt
prompt = f"""LIST ALL OF THESE GAMES: {slate_info}.
For EVERY SINGLE GAME listed above, provide HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team.
Do not skip any games. Do not summarize. 
Return ONLY a valid JSON object.
Format: {{"Away Team @ Home Team": [{"name": "Player", "hrr": 2.5}]}}
"""

# 4. Ask and Save
try:
    response = model.generate_content(prompt)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    
    with open("data.json", "w") as f:
        f.write(clean_json)
    print(f"Success: Processed {len(active_games)} games.")
except Exception as e:
    print(f"Error: {e}")
    with open("data.json", "w") as f:
        f.write("{}")
