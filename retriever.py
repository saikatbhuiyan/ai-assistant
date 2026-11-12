import re
from pathlib import Path

# The knowledge folder next to this file, so it's found whichever folder
# the program is run from.
KNOWLEDGE_FOLDER = Path(__file__).parent / 'knowledge'

# Common words that appear in almost every question, so they say nothing
# about which document is relevant.
STOP_WORDS = {
    "a", "about", "an", "and", "are", "can", "do", "does", "explain", "for",
    "how", "i", "in", "is", "it", "me", "of", "tell", "the", "to", "what",
    "which", "who", "why",
}


def load_documents(directory: str | Path = KNOWLEDGE_FOLDER) -> dict:
    """
    Load documents from a specified directory.

    Args:
        directory (str | Path): The path to the directory containing documents.

    Returns:
        dict: A dictionary where keys are document names and values are their content.
              Documents are in alphabetical order, so results are the same on every computer.
    """
    documents = {}

    folder = Path(directory)

    for file in sorted(folder.glob('*.txt')):
        documents[file.name] = file.read_text(
            encoding='utf-8'
        )

    return documents


def find_words(text: str) -> set:
    """Return the set of lowercase words in text, ignoring punctuation."""

    return set(re.findall(r"\w+", text.lower()))


def retrieve(question: str, directory: str | Path = KNOWLEDGE_FOLDER):
    """
    Retrieve the document that shares the most words with a question.

    Args:
        question (str): The question to search for in the documents.
        directory (str | Path): The path to the directory containing documents.

    Returns:
        tuple: A tuple containing the filename and content of the best matching document,
               or (None, None) if no document shares a word with the question.
               Ties go to the file that comes first alphabetically.
    """
    question_words = find_words(question) - STOP_WORDS

    best_filename, best_content, best_score = None, None, 0

    for filename, content in load_documents(directory).items():
        score = len(question_words & find_words(content))

        if score > best_score:
            best_filename, best_content, best_score = filename, content, score

    return best_filename, best_content
