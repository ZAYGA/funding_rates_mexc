import requests
import time
import hmac
import hashlib
from datetime import datetime
API_KEY = 'API_KEY'
SECRET_KEY = 'SECRET_KEY'
FUNDING_RATE_URL = "https://contract.mexc.com/api/v1/contract/funding_rate"
WEBHOOK_URL = "" # Enter your webhook link here
def get_token_url(symbol):
    return f"https://futures.mexc.com/exchange/{symbol}"
def format_discord_embed(symbol, funding_rate, next_funding_rate_time, plus=""):
    timestamp = f"<t:{int(next_funding_rate_time / 1000)}:R>" if next_funding_rate_time else "No data available"
    symbol_display = f"[{symbol.replace('_', '/')}](https://futures.mexc.com/exchange/{symbol})"
    rate_display = f"{plus}{funding_rate * 100:.2f}%"
    rate_display_leveraged = f"{plus}{(funding_rate * 100)*20:.2f}%"
    if abs(funding_rate) >= 0.0012:
        return f"**{timestamp}┃{rate_display}┃{symbol_display}┃{rate_display} → {rate_display_leveraged}**"
    else:
        return f"{timestamp}┃{rate_display}┃{symbol_display}┃{rate_display} → {rate_display_leveraged}"
def get_signature(timestamp):
    query_string = f"timestamp={timestamp}"
    return hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
def fetch_data():
    timestamp = int(time.time() * 1000)
    params = {'timestamp': timestamp, 'signature': get_signature(timestamp)}
    headers = {'X-MEXC-APIKEY': API_KEY, 'Content-Type': 'application/json'}
    response = requests.get(FUNDING_RATE_URL, headers=headers, params=params)
    return response
def post_discord(embed):
    response = requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"{current_time} • {'Succes' if response.status_code == 204 else f'Error : {response.status_code} - {response.text}'}")
def execute_script():
    response = fetch_data()
    if response.status_code == 200:
        data = response.json()['data']
        rates = [(item['symbol'], float(item['fundingRate']), item.get('nextSettleTime')) for item in data]
        positive_rates = "\n".join([format_discord_embed(*rate, "+") for rate in sorted(rates, key=lambda x: x[1], reverse=True)[:10]])
        negative_rates = "\n".join([format_discord_embed(*rate) for rate in sorted(rates, key=lambda x: x[1])[:10]])
        current_time = datetime.now().strftime("%H:%M:%S")
        embed = {
            "description": "<:mexc:1279203892197855312> **Funding Rates MEXC**",
            "color": 0x2c75ff,
            "fields": [{"name": "<:positif:1279203868172878048>", "value": positive_rates},
                       {"name": "<:negatif:1279203880583827507>", "value": negative_rates}],
            "footer": {"text": f"@Cryptotenyx X Zayga • Today at {current_time}"}
        }
        post_discord(embed)
    else:
        print(f"Error : {response.status_code}, {response.text}")
while True:
    execute_script()
    time.sleep(600)