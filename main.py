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

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

bonus_id_pattern = re.compile(r'\"(\d+)\"')
prefix_pattern = re.compile(r'\[(.*)]')
suffix_pattern = re.compile(r'\((.*)\)')


def float_value_from_money_string(money):
    return float((money[2:]).replace(',', ''))


def format_money_from_float_value(value):
    if value >= 100:
        formatted_value = f'{value:,.0f}'
    else:
        formatted_value = f'{value:.2f}'
    return f'$ {formatted_value}'


def float_value_from_multiplier_string(multiplier):
    return float(multiplier.replace('x', '').replace(',', '').strip())


def format_multiplier_from_float_value(value):
    if value >= 1000:
        formatted_value = f'{value:,.0f}'
    elif value >= 10:
        formatted_value = f'{value:.0f}'
    else:
        formatted_value = f'{value:.1f}'
    return f'{formatted_value} X'


def get_bht_statistic(statistic):
    # Get the JSON from the request
    url = f"{bht_url}/{statistic}/{bht_token}"
    response = requests.request("GET", url, headers={'x-requested-with': 'XMLHttpRequest'}, data={})
    if response.status_code != 200:
        return None
    json_data = response.json()

    # Loop over all the bonuses
    if statistic == 'bonus_list':
        payout_bonus_count = 0
        for idx in range(len(json_data['bonuses'])):

            # Multi calculation and formatting
            json_data['bonuses'][idx]['multiplier_value'] = None
            json_data['bonuses'][idx]['multiplier'] = None

            if json_data['bonuses'][idx]['payout'] is not None and json_data['bonuses'][idx]['bet_size'] is not None:
                multi = float((json_data['bonuses'][idx]['payout'][2:]).replace(',', '')) / float((json_data['bonuses'][idx]['bet_size'][2:]).replace(',', ''))

                json_data['bonuses'][idx]['multiplier_value'] = multi
                json_data['bonuses'][idx]['multiplier'] = format_multiplier_from_float_value(multi)

            # Count the number of bonuses with a payout
            if json_data['bonuses'][idx]['payout'] is not None:
                payout_bonus_count += 1

        # Bonus progress calculation and formatting
        json_data['bonus_progress_value'] = 0
        if payout_bonus_count > 0:
            bonus_progress = float(payout_bonus_count) / float(len(json_data['bonuses'])) * 100
            json_data['bonus_progress_value'] = f'{bonus_progress:.0f}'

            # Other Money formatting
            json_data['info_start_cost'] = format_money_from_float_value(
                float_value_from_money_string(json_data['info_start_cost']))
            json_data['info_amount_won'] = format_money_from_float_value(
                float_value_from_money_string(json_data['info_amount_won']))
            json_data['highest_payout_value'] = format_money_from_float_value(
                float_value_from_money_string(json_data['highest_payout_value']))
            json_data['highest_payout_betsize'] = format_money_from_float_value(
                float_value_from_money_string(json_data['highest_payout_betsize']))
            json_data['highest_multi_betsize'] = format_money_from_float_value(
                float_value_from_money_string(json_data['highest_multi_betsize']))

            # Other Multiplier formatting
            json_data['info_required_average'] = format_multiplier_from_float_value(
                float_value_from_multiplier_string(json_data['info_required_average']))
            json_data['info_running_average'] = format_multiplier_from_float_value(
                float_value_from_multiplier_string(json_data['info_running_average']))
            json_data['highest_multi_value'] = format_multiplier_from_float_value(
                float_value_from_multiplier_string(json_data['highest_multi_value']))


        # PART 2
        # Get the HTML from the bonus_list widget, for the BEFORE and AFTER values
        html = requests.request("GET", url, headers={}, data={})
        if html.status_code != 200:
            return json_data

        lines = html.text.splitlines()
        for index in range(len(lines)):

            # Prefix and Suffix parsing
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

                for idy in range(len(json_data['bonuses'])):
                    if str(json_data['bonuses'][idy]['id']) == bonus_id:
                        json_data['bonuses'][idy]['prefix'] = prefix
                        json_data['bonuses'][idy]['suffix'] = suffix

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
