import os
import dotenv
import fastapi
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

dotenv.load_dotenv()

BHT_URL = os.getenv("BHT_URL")
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://markmolenmaker.github.io",
    "https://markmolenmaker.github.io"
    ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)


def get_bht_bonus_list(statistic_url):
    # Get the HTML from the request
    url = f"{BHT_URL}{statistic_url}"
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


def get_bht_statistic(statistic_url):
    # Get the HTML from the request
    url = f"{BHT_URL}{statistic_url}"
    response = requests.request("GET", url, headers={}, data={})
    html = response.text

    # Get the value from the HTML
    for line in html.splitlines():
        line = line.strip()
        if '<span class="value-show">' in line:
            value = line[25:-7]
            return value

    return None


BHT_DIFFERENTLY_FORMATTED = {
    "bonus_list": get_bht_bonus_list
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/statistic/{statistic}")
async def get_statistic(statistic: str):
    statistic_url = os.getenv(statistic.capitalize())
    if statistic_url is None:
        raise HTTPException(status_code=404, detail=f"No endpoint for: {statistic}, was found!")

    # Intercept if statistic is special
    if statistic in BHT_DIFFERENTLY_FORMATTED.keys():
        value = BHT_DIFFERENTLY_FORMATTED[statistic](statistic_url)
    else:
        value = get_bht_statistic(statistic_url)

    if value is None:
        raise HTTPException(status_code=400, detail="Could not extract a value from the HTML.")

    return fastapi.Response(content=json.dumps({
        "statistic": statistic,
        "value": value
    }), media_type="application/json")
