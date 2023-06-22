import fastapi
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json


def get_bht_bonus_list(statistic):
    # Get the HTML from the request
    url = f"{bht_url}/{statistic}/{bht_endpoints[statistic]}"
    response = requests.request("GET", url, headers={}, data={})
    html = response.text

    # Get the bonus_list contents from the HTML
    bonus_list = []
    lines = html.splitlines()
    for index in range(len(lines)):
        line = lines[index].strip()
        if line.startswith('<div class="slot" data-bonusid'):
            bonus = {
                "id": line[32:-2],
                "index": int(lines[index + 2].strip()[:-1]),
                "slot": lines[index + 5].strip()[:-6].strip()
            }

            if lines[index + 6].strip().startswith('<div class="slot_betsize" data-betsize'):
                bonus["betsize"] = lines[index + 6].strip()[40:-2]
            if lines[index + 9].strip().startswith('<div class="slot_payout" data-payout'):
                bonus["payout"] = lines[index + 9].strip()[38:-2]

            bonus_list.append(bonus)

    return bonus_list


def get_bht_statistic(statistic):
    # Get the HTML from the request
    url = f"{bht_url}/{statistic}/{bht_endpoints[statistic]}"
    response = requests.request("GET", url, headers={}, data={})
    html = response.text

    # Get the value from the HTML
    for line in html.splitlines():
        line = line.strip()
        if '<span class="value-show">' in line:
            value = line[25:-7]
            return value

    return None

bht_url = "https://bht.bet/widgets"
bht_endpoints = {
    "amount_won": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "hunt_average_betsize": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "average_cost_per_bonus": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "average_current_multi": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "average_required_multi": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "bonus_list": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "bonus_count": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "bonus_remaining_count": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "cumulative_multi": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "current_average_money": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "current_average_required_money": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "profit_loss": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "rolling_required_average_to_be": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo",
    "start_cost": "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo"
}
bht_specifics = {
    "bonus_list": get_bht_bonus_list
}

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://markmolenmaker.github.io",
    "https://markmolenmaker.github.io"
    ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/statistic/{statistic}")
async def get_statistic(statistic: str):
    if statistic not in bht_endpoints.keys():
        raise HTTPException(status_code=404, detail=f"No endpoint for: {statistic}, was found!")

    # Intercept if statistic is special
    if statistic in bht_specifics.keys():
        value = bht_specifics[statistic](statistic)
    else:
        value = get_bht_statistic(statistic)

    if value is None:
        raise HTTPException(status_code=400, detail="Could not extract a value from the HTML.")

    return fastapi.Response(content=json.dumps({
        "statistic": statistic,
        "value": value
    }), media_type="application/json")
