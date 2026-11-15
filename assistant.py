from openai import OpenAI
from dotenv import load_dotenv
import asyncio
import os

from tools.tools import read_text_file
from planner import choose_tool

from mcp_tools.mcp_client import connect, disconnect, discover_tools, execute_tool

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

model = os.getenv("MODEL")

if not model:
    raise SystemExit("Set MODEL in the .env file, for example MODEL=qwen3:4b")

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


async def main():

    # Start the MCP server and ask which tools it offers
    mcp_client = await connect()

    try:
        # Only tools the server reports can run, whatever the planner replies
        tool_names = {tool.name for tool in await discover_tools(mcp_client)}

        while True:

            # input() in a thread, so it doesn't block the MCP connection
            user_input = (await asyncio.to_thread(input, "\nYou : ")).strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("\nAI  : Goodbye! Have a great day.")
                break

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

            # The planner decides which tool to use, if any
            tool_name = choose_tool(user_input)

            if tool_name in tool_names:
                tool_response = await execute_tool(mcp_client, tool_name)
                print("\nAI :", f"Tool Response: {tool_response}")
                continue

            # Save the user's message
            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(model=model, messages=messages)

            ai_reply = response.choices[0].message.content

            print("\nAI :", ai_reply)

            # Save the AI's reply
            messages.append({"role": "assistant", "content": ai_reply})

    finally:
        # Also runs after an error or Ctrl+C, so the server is always stopped
        await disconnect(mcp_client)


asyncio.run(main())
