import urllib.request
import urllib.parse
import json

def fetch_weather():
    lat = -33.8688
    lon = 151.2093
    city = "Sydney"
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
        req2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req2, timeout=5) as response:
            w_data = json.loads(response.read().decode())
        print(json.dumps(w_data, indent=2))
    except Exception as e:
        print("Error:", str(e))

fetch_weather()
