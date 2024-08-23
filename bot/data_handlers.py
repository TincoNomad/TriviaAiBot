import requests #type: ignore
import json
from config import LEADERBOARD_URL, SCORE_URL
from .utils import logger

# Fetch and format the leaderboard data
def get_score():
    try:
        response = requests.get(LEADERBOARD_URL)
        response.raise_for_status()
        json_data = response.json()
        
        if not isinstance(json_data, list):
            raise ValueError("La respuesta no es una lista de diccionarios")
        
        leaderboard = ""
        for id, item in enumerate(json_data, start=1):
            if not isinstance(item, dict):
                raise ValueError("Un elemento de la lista no es un diccionario")
            leaderboard += f"{id} - {item['name']} - {item['points']} Points\n"
        
        return leaderboard if leaderboard else "No hay puntuaciones aún, no se han jugado partidas"
    
    except requests.RequestException as e:
        logger.error(f"Error al obtener puntuaciones: {e}")
        return f"Error al obtener puntuaciones: {e}"
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f"Error al procesar los datos de puntuación: {e}")
        return f"Error al procesar los datos de puntuación: {e}"

# Update player's score in the database
def update_score(name, points):
    url = SCORE_URL
    new_score = {"name": name, "points": points}
    response = requests.post(url, data=new_score)
    return response.status_code