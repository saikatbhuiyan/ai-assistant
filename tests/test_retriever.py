import tempfile
import unittest
from pathlib import Path

from retriever import load_documents, retrieve


class RetrieverTestCase(unittest.TestCase):
    """Builds a small knowledge folder in a temporary directory for each test."""

    files = {
        "weather.txt": "Weather forecasting predicts future atmospheric conditions.",
        "python.txt": "Python is a high-level programming language used for Machine Learning.",
        "machine_learning.txt": "Machine Learning is a branch of Artificial Intelligence.",
        "mysql.txt": "MySQL is a relational database. SQL is used to query data.",
    }

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = temp.name

        # Written in non-alphabetical order on purpose
        for name, text in self.files.items():
            Path(self.folder, name).write_text(text, encoding="utf-8")

        Path(self.folder, "notes.md").write_text("Python notes", encoding="utf-8")


class TestLoadDocuments(RetrieverTestCase):

    def test_loads_every_text_file_with_its_content(self):
        documents = load_documents(self.folder)

        self.assertEqual(documents, self.files)

    def test_ignores_files_that_are_not_text_files(self):
        self.assertNotIn("notes.md", load_documents(self.folder))

    def test_documents_are_in_alphabetical_order(self):
        names = list(load_documents(self.folder))

        self.assertEqual(names, sorted(names))


class TestRetrieve(RetrieverTestCase):

    def assertRetrieves(self, question, expected_name):
        name, content = retrieve(question, self.folder)

        self.assertEqual(name, expected_name)
        self.assertEqual(content, self.files.get(expected_name))

    def test_finds_a_single_keyword(self):
        self.assertRetrieves("weather", "weather.txt")

    def test_ignores_case(self):
        self.assertRetrieves("PYTHON", "python.txt")

    def test_finds_a_whole_question(self):
        for question, expected in [
            ("Tell me about Python", "python.txt"),
            ("What is MySQL?", "mysql.txt"),
            ("python?", "python.txt"),
        ]:
            with self.subTest(question=question):
                self.assertRetrieves(question, expected)

    def test_matches_whole_words_only(self):
        # "sql" is inside "mysql", but only mysql.txt has SQL as its own word
        self.assertRetrieves("sql", "mysql.txt")

    def test_prefers_the_document_matching_more_words(self):
        # Both mention machine learning; only one mentions artificial intelligence
        self.assertRetrieves(
            "machine learning and artificial intelligence", "machine_learning.txt"
        )

    def test_ties_go_to_the_alphabetically_first_file(self):
        self.assertRetrieves("machine learning", "machine_learning.txt")

    def test_returns_none_when_nothing_matches(self):
        self.assertRetrieves("Will it rain tomorrow?", None)

    def test_common_words_alone_match_nothing(self):
        self.assertRetrieves("What is it?", None)

    # Known limitation of keyword search: "coding" never appears in the text,
    # so meaning-based search (embeddings) is needed to find python.txt.
    @unittest.expectedFailure
    def test_finds_a_synonym(self):
        self.assertRetrieves("coding", "python.txt")


if __name__ == "__main__":
    unittest.main()
