import os
import requests
import json
import google.generativeai as genai

# 1. Get MLB Data
try:
    response = requests.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1")
    response.raise_for_status()
    games = response.json().get('dates', [{}])[0].get('games', [])
    slate_info = "\n".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in games])
except Exception as e:
    slate_info = "Current MLB Slate"

# 2. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = f"""Using this MLB slate: {slate_info}, calculate HRR projections (Hits + Runs + RBIs) for the top 5 hitters on each team. 
Return ONLY a valid JSON object where keys are game names (e.g., 'NYY @ BOS') and values are lists of objects with 'name' and 'hrr' keys. 
Do not include markdown formatting or extra text."""

# 3. Ask Gemini
response = model.generate_content(prompt)
clean_json = response.text.replace('```json', '').replace('```', '').strip()

# 4. Save
with open("data.json", "w") as f:
    f.write(clean_json)

print("Successfully updated data.json via Gemini")
