from discord import Message, Client, DMChannel
from ..api_client import TriviaAPIClient
from ..utils.logging_bot import command_logger
from typing import Dict, Any, List, Optional

class TriviaUpdater:
    def __init__(self, client: Client):
        self.client = client
        self.api_client = TriviaAPIClient()
        
    async def handle_list_trivias(self, message: Message) -> Optional[List[Dict[str, Any]]]:
        """Handles listing trivias for a user through DM"""
        try:
            username = message.author.name
            command_logger.info(f"Listing trivias for user: {username}")
            
            # Send initial message to original channel
            await message.channel.send("I've sent you a DM to update your trivia!")
            
            params: Dict[str, str] = {"username": username}
            trivias: List[Dict[str, Any]] = await self.api_client.get_user_trivias(params)
            
            if not trivias:
                await message.author.send("You don't have any trivias created yet.")
                return None
                
            trivia_list = "\n".join(
                f"{i+1}. {trivia['title']} - Difficulty: {trivia['difficulty']} - Theme: {trivia['theme']}"
                for i, trivia in enumerate(trivias)
            )
            
            await message.author.send(f"Your trivias:\n```\n{trivia_list}\n```")
            return trivias
            
        except Exception as e:
            command_logger.error(f"Error listing trivias: {e}")
            await message.author.send("Error getting the list of trivias.")
            return None
            
    async def handle_update_trivia(self, message: Message) -> None:
        """Handles updating a trivia through DM"""
        try:
            trivias = await self.handle_list_trivias(message)
            if not trivias:
                return
            
            # Select trivia
            await message.author.send("Which trivia would you like to update? (Enter the number)")
            
            def check(m):
                return m.author == message.author and isinstance(m.channel, DMChannel) and m.content.isdigit()
                
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            trivia_index = int(response.content) - 1
            
            if trivia_index < 0 or trivia_index >= len(trivias):
                await message.author.send("Invalid trivia number.")
                return
                
            selected_trivia = trivias[trivia_index]
            
            # Show update options
            await message.author.send(
                "What would you like to update?\n"
                "1. Title\n"
                "2. Difficulty (1-5)\n"
                "3. Theme\n"
                "4. Questions and Answers"
            )
            
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            field_choice = int(response.content)
            
            if field_choice == 4:
                # Show existing questions
                questions = selected_trivia.get('questions', [])
                questions_list = "\n".join(
                    f"{i+1}. {q['question_title']}"
                    for i, q in enumerate(questions)
                )
                await message.author.send(f"Current questions:\n```\n{questions_list}\n```")
                
                # Select question
                await message.author.send("Which question would you like to edit? (Enter the number)")
                response = await self.client.wait_for('message', timeout=30.0, check=check)
                question_index = int(response.content) - 1
                
                if question_index < 0 or question_index >= len(questions):
                    await message.author.send("Invalid question number.")
                    return
                    
                selected_question = questions[question_index]
                
                # Question edit options
                await message.author.send(
                    "What would you like to edit?\n"
                    "1. Question text\n"
                    "2. Correct answer\n"
                    "3. Incorrect answers"
                )
                
                response = await self.client.wait_for('message', timeout=30.0, check=check)
                question_field = int(response.content)
                
                if question_field == 1:
                    await message.author.send("Enter the new question text:")
                    response = await self.client.wait_for('message', timeout=60.0, check=check)
                    selected_question['question_title'] = response.content
                    
                elif question_field in [2, 3]:
                    answers = selected_question.get('answers', [])
                    if question_field == 2:
                        # Edit correct answer
                        correct_answer = next((a for a in answers if a['is_correct']), None)
                        if correct_answer:
                            await message.author.send("Enter the new correct answer:")
                            response = await self.client.wait_for('message', timeout=60.0, check=check)
                            correct_answer['answer_title'] = response.content
                            
                    else:
                        # Edit incorrect answers
                        incorrect_answers = [a for a in answers if not a['is_correct']]
                        incorrect_list = "\n".join(
                            f"{i+1}. {a['answer_title']}"
                            for i, a in enumerate(incorrect_answers)
                        )
                        await message.author.send(f"Current incorrect answers:\n```\n{incorrect_list}\n```")
                        
                        await message.author.send("Which incorrect answer would you like to edit? (Enter the number)")
                        response = await self.client.wait_for('message', timeout=30.0, check=check)
                        answer_index = int(response.content) - 1
                        
                        if answer_index < 0 or answer_index >= len(incorrect_answers):
                            await message.author.send("Invalid answer number.")
                            return
                            
                        await message.author.send("Enter the new incorrect answer:")
                        response = await self.client.wait_for('message', timeout=60.0, check=check)
                        incorrect_answers[answer_index]['answer_title'] = response.content
                
                # Prepare question update data
                questions_data = [{
                    "id": selected_question["id"],
                    "question_title": selected_question["question_title"],
                    "answers": selected_question["answers"]
                }]
                
                # Send update to API
                await self.api_client.update_trivia_questions(selected_trivia["id"], questions_data)
                
            else:
                # Handle basic fields
                field_mapping = {
                    1: "title",
                    2: "difficulty",
                    3: "theme"
                }
                
                await message.author.send("Enter the new value:")
                response = await self.client.wait_for('message', timeout=60.0, check=check)
                new_value = response.content
                
                update_data = {
                    field_mapping[field_choice]: int(new_value) if field_choice == 2 else new_value
                }
                
                if field_choice == 2:
                    try:
                        difficulty = int(new_value)
                        if difficulty not in range(1, 6):
                            await message.author.send("Difficulty must be a number between 1 and 5.")
                            return
                    except ValueError:
                        await message.author.send("Difficulty must be a number.")
                        return
            
            # Send update to API
            await self.api_client.patch_trivia(selected_trivia["id"], update_data)
            await message.author.send("Trivia updated successfully!")
            
        except TimeoutError:
            await message.author.send("Time's up! Please try again.")
        except Exception as e:
            command_logger.error(f"Error updating trivia: {e}")
            await message.author.send("Error updating the trivia.")