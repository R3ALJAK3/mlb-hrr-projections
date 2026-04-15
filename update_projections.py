import os
import requests
import json
import google.generativeai as genai

# 1. Get COMPLETE MLB Data for the full day
try:
    # Adding the date and 'schedule' flag ensures we see games that haven't started yet
    url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=2026-04-15"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    games = []
    if 'dates' in data and len(data['dates']) > 0:
        games = data['dates'][0].get('games', [])
    
    # Filter for games that are NOT finished ('Final')
    active_games = [g for g in games if g.get('status', {}).get('abstractGameState') != 'Final']
    
    slate_info = "\n".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in active_games])
    
    if not slate_info:
        slate_info = "No more games scheduled for today."
except Exception as e:
    slate_info = "April 15, 2026 MLB Slate"

# 2. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = f"""Using this MLB slate: {slate_info}, calculate HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team. 
Return ONLY a valid JSON object where keys are game names (e.g., 'NYY @ BOS') and values are lists of objects with 'name' and 'hrr' keys. 
Do not include markdown formatting or extra text."""

# 3. Ask Gemini
try:
    response = model.generate_content(prompt)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    
    with open("data.json", "w") as f:
        f.write(clean_json)
    print(f"Successfully updated data.json with {len(active_games)} games.")
except Exception as e:
    print(f"Error: {e}")
    with open("data.json", "w") as f:
        f.write("{}")
