import unittest

from similarity import cosine_similarity


class TestCosineSimilarity(unittest.TestCase):

    def test_identical_vectors_score_1(self):
        self.assertAlmostEqual(cosine_similarity([1, 2, 3], [1, 2, 3]), 1.0)

    def test_length_does_not_matter_only_direction(self):
        self.assertAlmostEqual(cosine_similarity([1, 2, 3], [2, 4, 6]), 1.0)

    def test_unrelated_vectors_score_0(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_opposite_vectors_score_minus_1(self):
        self.assertAlmostEqual(cosine_similarity([1, 2], [-1, -2]), -1.0)

    def test_known_angle(self):
        # 45 degrees apart: cos(45°) = 0.7071...
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 1]), 0.70710678)

    def test_zero_vector_scores_0_instead_of_dividing_by_zero(self):
        self.assertEqual(cosine_similarity([0, 0, 0], [1, 2, 3]), 0.0)

    def test_closer_meaning_scores_higher(self):
        question = [0.9, 0.1, 0.0]
        related = [0.8, 0.2, 0.1]
        unrelated = [0.0, 0.1, 0.9]

        self.assertGreater(
            cosine_similarity(question, related),
            cosine_similarity(question, unrelated),
        )


if __name__ == "__main__":
    unittest.main()
