import fastapi
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

bht_url = "https://bht.bet/widgets"
bht_token = "9UTk18nl4UwzSYz4alwIHSUlNLsFfwQo"

app = FastAPI()

origins = ["http://localhost", "http://localhost:8080", "http://markmolenmaker.github.io", "https://markmolenmaker.github.io" ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)


def get_bht_statistic(statistic):
    # Get the JSON from the request
    url = f"{bht_url}/{statistic}/{bht_token}"
    response = requests.request("GET", url, headers={'x-requested-with': 'XMLHttpRequest'}, data={})

    if response.status_code != 200:
        return None
    return response.json()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/statistic/{statistic}")
async def get_statistic(statistic: str):
    bht_widget_content = get_bht_statistic(statistic)

    if bht_widget_content is None:
        raise HTTPException(status_code=400, detail=f"Could not retrieve the content of the {statistic} widget.")

    return fastapi.Response(content=json.dumps(bht_widget_content), media_type="application/json")
