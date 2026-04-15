import os
import requests
from anthropic import Anthropic

# 1. Get MLB Data for Today
response = requests.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1")
games = response.json().get('dates', [{}])[0].get('games', [])

# 2. Prepare data for Claude
slate_info = "\n".join([f"{g['teams']['away']['team']['name']} @ {g['teams']['home']['team']['name']}" for g in games])

# 3. Ask Claude to Project
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
prompt = f"Using this MLB slate: {slate_info}, calculate HRR projections for the top 5 hitters on each team based on 2026 park factors and pitching matchups. Return ONLY a JSON object."

message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}]
)

# 4. Save the Projections
with open("data.json", "w") as f:
    f.write(message.content[0].text)
