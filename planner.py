import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Create AI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

def choose_tool(user_request: str) -> str | None:
    """
    Choose the appropriate tool based on the user's request.

    Args:
        user_request (str): The user's request.

    Returns:
        str | None: The name of the chosen tool, or None if no tool is appropriate.
    """
    prompt = f"""
        You are an AI assistant that helps users choose the best tool for their needs. 
        Based on the user's request, you will select the most appropriate tool from the following options:

        1. get_current_time: Provides the current date and time.

        2. roll_dice: Simulates rolling a dice and returns a random number between 1 and 6.

        3. generate_password: Generates a random password based on specified criteria or Use when the user wants a secure password.

        if no tool is appropriate, respond with none.

        else, respond with the name of the tool that best fits the user's request.

        {user_request}
    """
    response = client.chat.completions.create(

        model= os.getenv("MODEL")  or "chatgpt-4o-latest",

        messages=[
            {
                "role":"system",
                "content":"You are an AI planner."
            },
            {
                "role":"user",
                "content": prompt
            }
        ]
    )
    
    content = response.choices[0].message.content

    return content.strip() if content else None
