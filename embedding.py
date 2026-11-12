from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

# Same Ollama server as the chat model, but a different model and endpoint
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(content):
    """
    Convert text into an embedding.

    Args:
        content (str): The text to convert.

    Returns:
        list: The embedding, a list of 768 numbers.
    """
    return client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=content
    ).data[0].embedding
