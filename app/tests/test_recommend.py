import pytest
from app.services.rec_engine import RecommendationEngine

@pytest.fixture
def rec_engine():
    return RecommendationEngine()

def test_recommendations(rec_engine):
    recs = rec_engine.get_recommendations("sneakers")
    assert len(recs) == 3
    assert all(isinstance(r, str) for r in recs)