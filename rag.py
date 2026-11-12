from openai import OpenAI
from dotenv import load_dotenv
import os
from retriever import load_documents

from embedding import create_embedding

from similarity import cosine_similarity

documents = load_documents()

if not documents:
    raise SystemExit("No .txt files found in the knowledge folder.")

document_embeddings = {}

for filename, content in documents.items():

    document_embeddings[filename] = create_embedding(content)

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

while True:

    user_input = input("\nYou : ").strip()

    if not user_input:
        continue

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    question_embedding = create_embedding(user_input)

    best_score = -1

    best_document = None

    for filename, embedding in document_embeddings.items():

        score = cosine_similarity(question_embedding, embedding)

        if score > best_score:

            best_score = score

            best_document = filename

    context = documents[best_document]

    prompt = f"""
                Answer the question using only
                the following information.

                If the answer is not in the information,
                say: 'I couldn't find that information
                in the knowledge base.'

                Context:

                {context}

                Question:

                {user_input}
            """

    response = client.chat.completions.create(
        model=os.getenv("MODEL"), messages=[{"role": "user", "content": prompt}]
    )

    print("\nAI :", response.choices[0].message.content)

    # Show where the answer came from, to check the retrieval step
    print(f"\n(Source: {best_document}, similarity {best_score:.2f})")
