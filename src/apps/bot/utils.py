# bot/utils.py

import requests


ENDPOINT_DOLLAR = "http://127.0.0.1:9001/api/v1/packages/get-sale-price"
ENDPOINT_COURT = "http://127.0.0.1:9001/api/v1/courts/{court_id}/disabled-hours/?date={date}"


async def fetch_dollar_price():
    response = requests.get(ENDPOINT_DOLLAR)
    return response.json()


async def fetch_disabled_court_hours(court_id, date):
    response = requests.get(
        ENDPOINT_COURT.format(court_id=court_id, date=date)
    )
    return response.json()
