import json
import aiohttp
from config import QUESTION_URL
from .utils import logger, School, Difficulty, POINTS_PER_CORRECT_ANSWER

class TriviaGame:
    def __init__(self):
        self.game_data = None

    async def fetch_game_data(self):
        try:
            print(f"Intentando obtener datos del juego desde: {QUESTION_URL}")
            async with aiohttp.ClientSession() as session:
                async with session.get(QUESTION_URL) as response:
                    print(f"Código de estado de la respuesta: {response.status}")
                    response.raise_for_status()
                    self.game_data = await response.json()
            print(f"Datos del juego cargados: {self.game_data[:100]}...")  # Imprime los primeros 100 caracteres
            logger.info("Datos del juego cargados exitosamente")
        except aiohttp.ClientError as e:
            print(f"Error de cliente aiohttp: {e}")
            logger.error(f"Error al obtener los datos del juego: {e}")
            raise Exception(f"Error al obtener los datos del juego: {e}")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            logger.error(f"Error al decodificar los datos del juego: {e}")
            raise Exception(f"Error al decodificar los datos del juego: {e}")

    def get_course(self, school_option, difficulty_level):
        if not self.game_data:
            raise Exception("Los datos del juego no han sido cargados")

        course = ""
        numero = 0
        for item in self.game_data:
            if item["school"] == School(int(school_option)).value and item["difficulty"] == Difficulty(int(difficulty_level)).value:
                numero += 1
                course += f"\n{numero}-{item['title']}"

        if not course:
            return "Ups, esto es vergonzoso, pero parece que aún no tenemos cursos con esas categorías 😅", 0
        
        return course, numero

    def get_question(self, selected_course, question_counter):
        if not self.game_data:
            raise Exception("Los datos del juego no han sido cargados")

        questionOptions = [i["question"] for i in self.game_data if i["title"] == selected_course]

        question = questionOptions[0][question_counter]["questionTitle"] + "\n\n"
        for id, item in enumerate(questionOptions[0][question_counter]["answer"], start=1):
            question += f"{id}-{item['answerTitle']}\n"

            if item["is_correct"]:
                answer = id
        return question, answer, POINTS_PER_CORRECT_ANSWER

    def getLink(self, selected_course):
        if not self.game_data:
            raise Exception("Los datos del juego no han sido cargados")

        for i in self.game_data:
            if i["title"] == selected_course:
                return i["url"]
        return "No se encontró el enlace del curso"
