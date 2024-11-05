import json
import aiohttp
from api.django import QUESTION_URL
from .utils import logger, School, Difficulty, POINTS_PER_CORRECT_ANSWER

class TriviaGame:
    def __init__(self):
        self.game_data = None

    async def fetch_game_data(self):
        try:
            print(f"Trying to get game data from: {QUESTION_URL}")
            async with aiohttp.ClientSession() as session:
                async with session.get(QUESTION_URL) as response:
                    print(f"Response status code: {response.status}")
                    response.raise_for_status()
                    self.game_data = await response.json()
            print(f"Game data loaded: {self.game_data[:100]}...")  # Prints the first 100 characters
            logger.info("Game data loaded successfully")
        except aiohttp.ClientError as e:
            print(f"aiohttp client error: {e}")
            logger.error(f"Error getting game data: {e}")
            raise Exception(f"Error getting game data: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            logger.error(f"Error decoding game data: {e}")
            raise Exception(f"Error decoding game data: {e}")

    def get_course(self, school_option, difficulty_level):
        if not self.game_data:
            raise Exception("Game data not loaded")

        course = ""
        numero = 0
        for item in self.game_data:
            if item["school"] == School(int(school_option)).value and item["difficulty"] == Difficulty(int(difficulty_level)).value:
                numero += 1
                course += f"\n{numero}-{item['title']}"

        if not course:
            return "Ups, this is embarrassing, but it seems we don't have courses with those categories yet 😅", 0
        
        return course, numero

    def get_question(self, selected_course, question_counter):
        if not self.game_data:
            raise Exception("Game data not loaded")

        questionOptions = [i["question"] for i in self.game_data if i["title"] == selected_course]

        question = questionOptions[0][question_counter]["questionTitle"] + "\n\n"
        for id, item in enumerate(questionOptions[0][question_counter]["answer"], start=1):
            question += f"{id}-{item['answerTitle']}\n"

            if item["is_correct"]:
                answer = id
        return question, answer, POINTS_PER_CORRECT_ANSWER

    def getLink(self, selected_course):
        if not self.game_data:
            raise Exception("Game data not loaded")

        for i in self.game_data:
            if i["title"] == selected_course:
                return i["url"]
        return "Course link not found"
