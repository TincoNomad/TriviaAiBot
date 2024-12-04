import requests #type: ignore
import json
from api.django import LEADERBOARD_URL, SCORE_URL
from .utils.logging_bot import bot_logger

# Fetch and format the leaderboard data
def get_score():
    try:
        response = requests.get(LEADERBOARD_URL)
        response.raise_for_status()
        json_data = response.json()
        
        if not isinstance(json_data, list):
            raise ValueError("The response is not a list of dictionaries")
        
        leaderboard = ""
        for id, item in enumerate(json_data, start=1):
            if not isinstance(item, dict):
                raise ValueError("An element of the list is not a dictionary")
            leaderboard += f"{id} - {item['name']} - {item['points']} Points\n"
        
        return leaderboard if leaderboard else "No scores yet, no games have been played"
    
    except requests.RequestException as e:
        bot_logger.error(f"Error getting scores: {e}")
        return f"Error getting scores: {e}"
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        bot_logger.error(f"Error processing scores data: {e}")
        return f"Error processing scores data: {e}"

# Update player's score in the database
def update_score(name, points):
    url = SCORE_URL
    new_score = {"name": name, "points": points}
    response = requests.post(url, data=new_score)
    return response.status_code