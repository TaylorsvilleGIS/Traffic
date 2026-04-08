import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# Taylorsville forecast endpoint
url = "https://api.weather.gov/gridpoints/SLC/98,171/forecast"

response = requests.get(url)

if response.status_code != 200:
    print("Weather API failed")
    exit()

data = response.json()

# First 5 forecast periods
periods = data['properties']['periods'][:5]

# Timestamp
now = datetime.now(ZoneInfo("America/Denver")).strftime("%m/%d/%Y %I:%M %p %Z")

# HTML content
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    font-family: Avenir Next, sans-serif;
    color: #fdf0d5;
}}

.weather {{
    padding: 10px;
}}

.period {{
    margin-bottom: 10px;
}}

hr {{
    border: 0;
    border-top: 1px solid #555;
}}
</style>
</head>

<body>
<div class="weather">

<p><strong>Updated:</strong> {now}</p>
"""

for p in periods:
    html_content += f"""
    <div class="period">
        <strong>{p['name']}</strong><br>
        Temp: {p['temperature']} {p['temperatureUnit']}<br>
        Wind: {p['windSpeed']} {p['windDirection']}<br>
        {p['shortForecast']}
    </div>
    <hr>
    """

html_content += """
</div>
</body>
</html>
"""

with open("weather.html", "w") as f:
    f.write(html_content)

print("Weather updated")
