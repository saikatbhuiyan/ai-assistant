from openai import OpenAI
from dotenv import load_dotenv
import os

from tools.tool_manager import execute_tool
from tools.tools import read_text_file
from planner import choose_tool

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

# Prompts for the file commands, e.g. "summarize notes.txt" or
# "ask project.txt Who worked on the project?"
file_prompts = {
    "summarize": "Summarize the following text in a concise manner:\n\n{document}",
    "explain": "Explain the following text in a simple and easy-to-understand manner:\n\n{document}",
    "ask": (
        "You are given a document.\n\n"
        "Answer the user's question using only the information present in the document.\n\n"
        "If the answer is not available, say: 'I couldn't find that information in the document.'\n\n"
        "Document:\n\n{document}\n\n"
        "Question:\n\n{question}"
    ),
}


while True:

    model = os.getenv("MODEL") or "chatgpt-4o-latest"

    user_input = input("\nYou : ")

    parts = user_input.split(maxsplit=2)
    command = parts[0].lower().rstrip(":") if parts else ""

    if command in file_prompts and len(parts) >= 2 and parts[1].endswith(".txt"):
        filename = parts[1]
        question = parts[2] if len(parts) == 3 else ""
        path = "data/" + filename

        # Only read files that sit directly inside the data folder
        if os.path.basename(filename) != filename or not os.path.isfile(path):
            print(f"\nAI : I couldn't find {filename} in the data folder.")
            continue

        if command == "ask" and not question:
            print(
                "\nAI : Add a question, for example: ask project.txt Who worked on the project?"
            )
            continue

        prompt = file_prompts[command].format(
            document=read_text_file(path), question=question
        )

        # A separate request, so the conversation history is left untouched
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        print("\nAI :", response.choices[0].message.content)
        continue

    tool_response = execute_tool(user_input)

    if not tool_response:
        tool_name = choose_tool(user_input)
        if tool_name:
            tool_response = execute_tool(user_input, tool_name=tool_name)

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
