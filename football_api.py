# football_api.py
import requests
from config import API_KEY

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

def fetch_matches_by_code_or_id(code_or_id, status="FINISHED", dateFrom=None, dateTo=None):
    league_id = find_league_id(code_or_id)
    if not league_id:
        return None

    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}competitions/{league_id}/matches"
    params = {"status": status}

    if dateFrom:
        params["dateFrom"] = dateFrom
    if dateTo:
        params["dateTo"] = dateTo

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    return response.json()

def find_league_id(code_or_id):
    competitions = fetch_competitions()
    for comp in competitions['competitions']:
        if comp['code'] == code_or_id or comp['id'] == code_or_id:
            return comp['id']
    return None

def fetch_all_matches():
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}matches"
    response = requests.get(url, headers=headers)
    return response.json()