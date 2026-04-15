import os
import requests
import json
import google.generativeai as genai
from datetime import datetime

# 1. Automatically get today's date in YYYY-MM-DD format
today = datetime.now().strftime('%Y-%m-%d')

# 2. Get EVERY MLB Game for whatever today is
try:
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    games = data['dates'][0].get('games', []) if 'dates' in data and data['dates'] else []
    
    slate_info = "\n".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in games])
except Exception as e:
    slate_info = f"MLB Slate for {today}"

# 3. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Prompt for the Full Slate
prompt = f"""Using this MLB slate for {today}: {slate_info}, calculate HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team. 
Return ONLY a valid JSON object. Include EVERY game listed. 
Do not include markdown formatting or any text other than the JSON."""

# 5. Ask and Save (This overwrites data.json automatically)
try:
    response = model.generate_content(prompt)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    
    with open("data.json", "w") as f:
        f.write(clean_json)
    print(f"Success: Processed {len(games)} games for {today}.")
except Exception as e:
    print(f"Error: {e}")
    # Fallback to empty JSON so the site doesn't crash
    with open("data.json", "w") as f:
        f.write("{}")
