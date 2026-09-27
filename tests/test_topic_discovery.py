"""Unit tests for Multi-Source Topic Discovery Engine."""

import pytest
from src.modules.research.topic_discovery import TopicDiscovery


def test_discover_topics_wikipedia():
    topics = TopicDiscovery.fetch_wikipedia_trending(limit=5)
    assert isinstance(topics, list)
    # Wikipedia API returns live items
    if topics:
        assert "title" in topics[0]
        assert "source" in topics[0]
        assert "engagement_score" in topics[0]


def test_discover_topics_for_niche():
    topics = TopicDiscovery.discover_topics_for_niche("dark_history", limit=5)
    assert isinstance(topics, list)
    assert len(topics) > 0
    first = topics[0]
    assert "title" in first
    assert len(first["title"]) > 5
    assert "source" in first
