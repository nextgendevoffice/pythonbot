# football_api.py
import requests
from config import API_KEY
from datetime import datetime

BASE_URL = "https://api.football-data.org/v4/"

def fetch_competitions():
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}competitions"
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_live_matches(competition_id=None):
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}matches?status=LIVE"
    if competition_id:
        url += f"&competitionId={competition_id}"
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_standings(competition_id):
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}competitions/{competition_id}/standings?=2022"
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_matches_by_date(competition_id, date):
    headers = {"X-Auth-Token": API_KEY}
    date_str = date.strftime("%Y-%m-%d")
    url = f"{BASE_URL}competitions/{competition_id}/matches?status=FINISHED&dateFrom={date_str}&dateTo={date_str}"
    response = requests.get(url, headers=headers)
    return response.json()

