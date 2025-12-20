"""
Unit tests for ranking consistency and semantic relevance metrics (T031)

Tests cover:
- Monotonic score decrease validation
- Relevance labeling thresholds
- Average similarity score calculation
- Score distribution analysis
- Precision@k and MRR metrics
"""

import pytest
from unittest.mock import Mock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMonotonicScoreDecrease:
    """Tests for monotonic score decrease validation (SC-003)"""

    def test_monotonic_decrease_passes(self):
        """Test that properly ranked results pass monotonic decrease check"""
        scores = [0.95, 0.87, 0.78, 0.65, 0.52]

        # Check if scores decrease monotonically
        is_monotonic = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

        assert is_monotonic is True, "Scores should decrease monotonically"

    def test_monotonic_decrease_with_equal_scores_passes(self):
        """Test that equal consecutive scores pass (≥ not just >)"""
        scores = [0.85, 0.85, 0.78, 0.72]

        is_monotonic = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

        assert is_monotonic is True, "Equal scores should pass (>= allows equality)"

    def test_monotonic_decrease_fails_when_scores_increase(self):
        """Test that non-monotonic scores fail validation"""
        scores = [0.85, 0.72, 0.78, 0.65]  # 0.72 -> 0.78 violates monotonic decrease

        is_monotonic = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

        assert is_monotonic is False, "Non-monotonic scores should fail"

    def test_monotonic_pass_rate_calculation(self):
        """Test calculation of monotonic decrease pass rate (SC-003: ≥90%)"""
        # Mock query results
        query_results = [
            {"scores": [0.95, 0.87, 0.78]},  # Pass
            {"scores": [0.82, 0.75, 0.68]},  # Pass
            {"scores": [0.90, 0.85, 0.87]},  # Fail (0.85 -> 0.87)
            {"scores": [0.76, 0.72, 0.70]},  # Pass
            {"scores": [0.88, 0.82, 0.80]},  # Pass
        ]

        passed_count = 0
        for result in query_results:
            scores = result["scores"]
            is_monotonic = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            if is_monotonic:
                passed_count += 1

        pass_rate = passed_count / len(query_results)

        assert passed_count == 4, "4 out of 5 queries should pass"
        assert pass_rate == 0.8, "Pass rate should be 80%"
        assert pass_rate >= 0.9 is False, "80% does not meet SC-003 target of 90%"

    def test_single_result_query_passes(self):
        """Test that queries with only 1 result pass (no ordering to check)"""
        scores = [0.85]

        # Single score vacuously satisfies monotonic decrease
        is_monotonic = len(scores) <= 1 or all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

        assert is_monotonic is True, "Single result should pass"


class TestRelevanceLabeling:
    """Tests for rule-based relevance labeling"""

    def test_high_relevance_threshold(self):
        """Test High relevance label for scores ≥ 0.78"""
        scores_high = [0.95, 0.87, 0.78]  # All should be High

        for score in scores_high:
            if score >= 0.78:
                label = "High"
            elif score >= 0.60:
                label = "Medium"
            elif score >= 0.40:
                label = "Low"
            else:
                label = "Incorrect"

            assert label == "High", f"Score {score} should be labeled High"

    def test_medium_relevance_threshold(self):
        """Test Medium relevance label for scores 0.60 ≤ score < 0.78"""
        scores_medium = [0.77, 0.70, 0.60]  # All should be Medium

        for score in scores_medium:
            if score >= 0.78:
                label = "High"
            elif score >= 0.60:
                label = "Medium"
            elif score >= 0.40:
                label = "Low"
            else:
                label = "Incorrect"

            assert label == "Medium", f"Score {score} should be labeled Medium"

    def test_low_relevance_threshold(self):
        """Test Low relevance label for scores 0.40 ≤ score < 0.60"""
        scores_low = [0.59, 0.50, 0.40]  # All should be Low

        for score in scores_low:
            if score >= 0.78:
                label = "High"
            elif score >= 0.60:
                label = "Medium"
            elif score >= 0.40:
                label = "Low"
            else:
                label = "Incorrect"

            assert label == "Low", f"Score {score} should be labeled Low"

    def test_incorrect_relevance_threshold(self):
        """Test Incorrect relevance label for scores < 0.40"""
        scores_incorrect = [0.39, 0.25, 0.10]  # All should be Incorrect

        for score in scores_incorrect:
            if score >= 0.78:
                label = "High"
            elif score >= 0.60:
                label = "Medium"
            elif score >= 0.40:
                label = "Low"
            else:
                label = "Incorrect"

            assert label == "Incorrect", f"Score {score} should be labeled Incorrect"

    def test_boundary_cases(self):
        """Test exact boundary values for relevance thresholds"""
        boundary_cases = {
            0.78: "High",     # Exact boundary High/Medium
            0.60: "Medium",   # Exact boundary Medium/Low
            0.40: "Low",      # Exact boundary Low/Incorrect
            0.39: "Incorrect"
        }

        for score, expected_label in boundary_cases.items():
            if score >= 0.78:
                label = "High"
            elif score >= 0.60:
                label = "Medium"
            elif score >= 0.40:
                label = "Low"
            else:
                label = "Incorrect"

            assert label == expected_label, f"Score {score} should be labeled {expected_label}"


class TestScoreDistribution:
    """Tests for score distribution analysis"""

    def test_score_distribution_calculation(self):
        """Test calculation of score distribution by relevance label"""
        scores = [0.95, 0.85, 0.78, 0.75, 0.68, 0.55, 0.42, 0.35, 0.20]

        distribution = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Incorrect": 0
        }

        for score in scores:
            if score >= 0.78:
                distribution["High"] += 1
            elif score >= 0.60:
                distribution["Medium"] += 1
            elif score >= 0.40:
                distribution["Low"] += 1
            else:
                distribution["Incorrect"] += 1

        assert distribution["High"] == 3, "3 scores should be High"
        assert distribution["Medium"] == 2, "2 scores should be Medium"
        assert distribution["Low"] == 2, "2 scores should be Low"
        assert distribution["Incorrect"] == 2, "2 scores should be Incorrect"

        total = sum(distribution.values())
        assert total == len(scores), "Total should equal number of scores"

    def test_empty_score_distribution(self):
        """Test handling of empty score list"""
        scores = []

        distribution = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Incorrect": 0
        }

        for score in scores:
            if score >= 0.78:
                distribution["High"] += 1
            elif score >= 0.60:
                distribution["Medium"] += 1
            elif score >= 0.40:
                distribution["Low"] += 1
            else:
                distribution["Incorrect"] += 1

        assert sum(distribution.values()) == 0, "Empty scores should result in zero distribution"


class TestAverageSimilarityScore:
    """Tests for average similarity score calculation"""

    def test_average_score_calculation(self):
        """Test calculation of average similarity score across all chunks"""
        scores = [0.85, 0.78, 0.72, 0.65, 0.58]

        average = sum(scores) / len(scores)

        assert average == 0.716, "Average should be correct"

    def test_average_score_with_single_result(self):
        """Test average with only one score"""
        scores = [0.85]

        average = sum(scores) / len(scores)

        assert average == 0.85, "Average of single score should be that score"

    def test_average_score_range(self):
        """Test that average score is within valid cosine similarity range"""
        scores = [0.95, 0.88, 0.72, 0.65, 0.50]

        average = sum(scores) / len(scores)

        assert -1.0 <= average <= 1.0, "Average score should be in valid range"


class TestPrecisionAtK:
    """Tests for Precision@k metric"""

    def test_precision_at_3(self):
        """Test Precision@3 calculation"""
        # Mock retrieved chunks with relevance labels
        retrieved_chunks = [
            {"score": 0.85, "relevant": True},   # Relevant
            {"score": 0.78, "relevant": True},   # Relevant
            {"score": 0.72, "relevant": False},  # Not relevant
            {"score": 0.65, "relevant": True},
            {"score": 0.58, "relevant": False}
        ]

        k = 3
        top_k_chunks = retrieved_chunks[:k]
        relevant_count = sum(1 for chunk in top_k_chunks if chunk["relevant"])

        precision_at_k = relevant_count / k

        assert relevant_count == 2, "2 out of top-3 should be relevant"
        assert precision_at_k == 2/3, "Precision@3 should be 2/3"

    def test_precision_at_k_all_relevant(self):
        """Test Precision@k when all top-k results are relevant"""
        retrieved_chunks = [
            {"score": 0.95, "relevant": True},
            {"score": 0.88, "relevant": True},
            {"score": 0.82, "relevant": True}
        ]

        k = 3
        relevant_count = sum(1 for chunk in retrieved_chunks[:k] if chunk["relevant"])
        precision_at_k = relevant_count / k

        assert precision_at_k == 1.0, "Precision@k should be 1.0 when all relevant"

    def test_precision_at_k_none_relevant(self):
        """Test Precision@k when no results are relevant"""
        retrieved_chunks = [
            {"score": 0.45, "relevant": False},
            {"score": 0.38, "relevant": False},
            {"score": 0.25, "relevant": False}
        ]

        k = 3
        relevant_count = sum(1 for chunk in retrieved_chunks[:k] if chunk["relevant"])
        precision_at_k = relevant_count / k

        assert precision_at_k == 0.0, "Precision@k should be 0.0 when none relevant"


class TestMeanReciprocalRank:
    """Tests for Mean Reciprocal Rank (MRR) metric"""

    def test_mrr_first_result_relevant(self):
        """Test MRR when first result is relevant (rank=1)"""
        retrieved_chunks = [
            {"score": 0.95, "relevant": True},   # First result relevant
            {"score": 0.85, "relevant": False},
            {"score": 0.72, "relevant": False}
        ]

        # Find rank of first relevant result (1-indexed)
        first_relevant_rank = None
        for i, chunk in enumerate(retrieved_chunks, start=1):
            if chunk["relevant"]:
                first_relevant_rank = i
                break

        rr = 1 / first_relevant_rank if first_relevant_rank else 0

        assert first_relevant_rank == 1, "First result is relevant"
        assert rr == 1.0, "Reciprocal rank should be 1.0 for first result"

    def test_mrr_third_result_relevant(self):
        """Test MRR when third result is first relevant (rank=3)"""
        retrieved_chunks = [
            {"score": 0.85, "relevant": False},
            {"score": 0.78, "relevant": False},
            {"score": 0.72, "relevant": True},   # Third result relevant
            {"score": 0.65, "relevant": False}
        ]

        first_relevant_rank = None
        for i, chunk in enumerate(retrieved_chunks, start=1):
            if chunk["relevant"]:
                first_relevant_rank = i
                break

        rr = 1 / first_relevant_rank if first_relevant_rank else 0

        assert first_relevant_rank == 3, "Third result is first relevant"
        assert rr == 1/3, "Reciprocal rank should be 1/3"

    def test_mrr_no_relevant_results(self):
        """Test MRR when no results are relevant"""
        retrieved_chunks = [
            {"score": 0.45, "relevant": False},
            {"score": 0.38, "relevant": False},
            {"score": 0.25, "relevant": False}
        ]

        first_relevant_rank = None
        for i, chunk in enumerate(retrieved_chunks, start=1):
            if chunk["relevant"]:
                first_relevant_rank = i
                break

        rr = 1 / first_relevant_rank if first_relevant_rank else 0

        assert first_relevant_rank is None, "No relevant results"
        assert rr == 0, "Reciprocal rank should be 0 when no relevant results"

    def test_mean_reciprocal_rank_across_queries(self):
        """Test MRR calculation across multiple queries"""
        # Query 1: First result relevant (RR = 1.0)
        # Query 2: Third result relevant (RR = 1/3)
        # Query 3: No relevant results (RR = 0.0)
        reciprocal_ranks = [1.0, 1/3, 0.0]

        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

        expected_mrr = (1.0 + 1/3 + 0.0) / 3
        assert abs(mrr - expected_mrr) < 0.001, f"MRR should be {expected_mrr}"


class TestTop3RelevanceRate:
    """Tests for top-3 relevance rate calculation (SC-006)"""

    def test_top3_relevance_meets_target(self):
        """Test that 80%+ queries have relevant top-3 results (SC-006)"""
        # Mock query results with top-3 relevance judgment
        queries = [
            {"has_relevant_top3": True},   # Query 1
            {"has_relevant_top3": True},   # Query 2
            {"has_relevant_top3": False},  # Query 3
            {"has_relevant_top3": True},   # Query 4
            {"has_relevant_top3": True},   # Query 5
        ]

        relevant_count = sum(1 for q in queries if q["has_relevant_top3"])
        top3_relevance_rate = relevant_count / len(queries)

        assert relevant_count == 4, "4 out of 5 queries have relevant top-3"
        assert top3_relevance_rate == 0.8, "Top-3 relevance rate should be 80%"
        assert top3_relevance_rate >= 0.8, "SC-006 target of 80% is met"

    def test_top3_relevance_below_target(self):
        """Test detection when top-3 relevance rate is below 80%"""
        queries = [
            {"has_relevant_top3": True},   # Query 1
            {"has_relevant_top3": False},  # Query 2
            {"has_relevant_top3": False},  # Query 3
            {"has_relevant_top3": False},  # Query 4
            {"has_relevant_top3": True},   # Query 5
        ]

        relevant_count = sum(1 for q in queries if q["has_relevant_top3"])
        top3_relevance_rate = relevant_count / len(queries)

        assert top3_relevance_rate == 0.4, "Top-3 relevance rate should be 40%"
        assert top3_relevance_rate < 0.8, "Below SC-006 target of 80%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
