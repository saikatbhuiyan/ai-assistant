from openai import OpenAI
from dotenv import load_dotenv
import os

from tools.tool_manager import execute_tool
from tools.tools import read_text_file

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

roles = {
    "1": "You are a friendly school teacher. Explain every concept using simple language and real-life examples.",
    "2": "You are a senior Python developer. Explain programming concepts clearly and always include Python examples.",
    "3": "You are an experienced travel guide. Recommend places, food, transportation and travel tips.",
    "4": "You are a motivational coach. Encourage the user and give practical advice with a positive attitude.",
    "5": "You are a professional interviewer. Ask one interview question at a time and provide feedback after each answer.",
}

print("\nChoose Your Assistant\n")

print("1. Teacher")
print("2. Python Expert")
print("3. Travel Guide")
print("4. Motivational Coach")
print("5. Interviewer")

choice = input("\nEnter your choice : ")

messages = [
    {"role": "system", "content": roles.get(choice, "You are a helpful AI assistant.")}
]


while True:

    model = os.getenv("MODEL")

    user_input = input("\nYou : ")

    text = user_input.lower()

    if text.startswith("summarize:"):
        filename = user_input[10:].strip()
        file_content = read_text_file("data/" + filename)

        prompt = f"""
        
        Summarize the following text in a concise manner:
        
        \n\n{file_content}
        """

        messages.append(
            {"role": "system", "content": "You are a helpful AI assistant."}
        )

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(model=model, messages=messages)

    if text.startswith("explain"):
        filename = user_input[7:].strip()
        file_content = read_text_file("data/" + filename)

        prompt = f"""
        
        Explain the following text in a simple and easy-to-understand manner:
        
        \n\n{file_content}
        """

        messages.append(
            {"role": "system", "content": "You are a helpful AI assistant."}
        )

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(model=model, messages=messages)

    if text.startswith("ask"):
        parts = user_input.split(maxsplit=2)
        # print(parts)
        filename = parts[1]
        question = parts[2]

        file_content = read_text_file("data/" + filename)

        prompt = f"""
                    You are given a document.

                    Answer the user's question using
                    only the information present
                    in the document.

                    If the answer is not available,
                    say:
                    'I couldn't find that information
                    in the document.'

                    Document:

                    {file_content}

                    Question:

                    {question}
                """
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(model=model, messages=messages)

        print(response.choices[0].message.content)
        continue

    tool_response = execute_tool(user_input)

    if tool_response:
        content = f"Tool Response: {tool_response}"
        print("\nAI :", content)
        continue

    # Save the user's message
    messages.append({"role": "user", "content": user_input})

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    response = client.chat.completions.create(model=model, messages=messages)

    ai_reply = response.choices[0].message.content

    print("\nAI :", ai_reply)

    # Save the AI's reply
    messages.append({"role": "assistant", "content": ai_reply})
