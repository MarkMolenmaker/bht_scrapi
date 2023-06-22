import fastapi
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

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

app = FastAPI()

origins = ["http://localhost", "http://localhost:8080", "http://markmolenmaker.github.io", "https://markmolenmaker.github.io" ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)


def get_bht_statistic(statistic):
    # Get the JSON from the request
    url = f"{bht_url}/{statistic}/{bht_endpoints[statistic]}"
    response = requests.request("GET", url, headers={'x-requested-with': 'XMLHttpRequest'}, data={})
    return response.json()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/statistic/{statistic}")
async def get_statistic(statistic: str):
    if statistic not in bht_endpoints.keys():
        raise HTTPException(status_code=404, detail=f"No endpoint for: {statistic}, was found!")

    bht_widget_content = get_bht_statistic(statistic)

    if bht_widget_content is None:
        raise HTTPException(status_code=400, detail=f"Could not retrieve the content of the {statistic} widget.")

    return fastapi.Response(content=json.dumps(bht_widget_content), media_type="application/json")
