import os
import re

from dotenv import load_dotenv
import fastapi
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

bht_url = "https://bht.bet/widgets"

# Get bht_token from command arguments parser

load_dotenv()
bht_token = os.environ.get("BHT_TOKEN")

app = FastAPI()

origins = ["http://localhost", "http://localhost:8080", "http://markmolenmaker.github.io", "https://markmolenmaker.github.io" ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

bonus_id_pattern = re.compile(r'\"(\d+)\"')
prefix_pattern = re.compile(r'\[(.*)]')
suffix_pattern = re.compile(r'\((.*)\)')


def get_bht_statistic(statistic):
    # Get the JSON from the request
    url = f"{bht_url}/{statistic}/{bht_token}"
    response = requests.request("GET", url, headers={'x-requested-with': 'XMLHttpRequest'}, data={})
    if response.status_code != 200:
        return None
    json_data = response.json()

    # Get the HTML from the bonus_list widget, for the BEFORE and AFTER values
    if statistic == 'bonus_list':
        html = requests.request("GET", url, headers={}, data={})
        if html.status_code != 200:
            return json_data

        lines = html.text.splitlines()
        for index in range(len(lines)):
            if 'class="slot" data-bonusid' in lines[index]:

                bonus_id, prefix, suffix = None, None, None

                match = bonus_id_pattern.search(lines[index])
                if match:
                    bonus_id = match.group(1)

                slot_line = lines[index + 5].strip()
                match = prefix_pattern.search(slot_line)
                if match:
                    prefix = match.group(1)

                match = suffix_pattern.search(slot_line)
                if match:
                    suffix = match.group(1)

                for idx in range(len(json_data['bonuses'])):
                    if str(json_data['bonuses'][idx]['id']) == bonus_id:
                        json_data['bonuses'][idx]['prefix'] = prefix
                        json_data['bonuses'][idx]['suffix'] = suffix

    return json_data


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/statistic/{statistic}")
async def get_statistic(statistic: str):
    bht_widget_content = get_bht_statistic(statistic)

    if bht_widget_content is None:
        raise HTTPException(status_code=400, detail=f"Could not retrieve the content of the {statistic} widget.")

    return fastapi.Response(content=json.dumps(bht_widget_content), media_type="application/json")
