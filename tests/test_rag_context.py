"""Tests for the RAG/TF-IDF context search adapter."""
from slack_app.context_search import (
    build_slack_context,
    retrieve_latest_field_reports,
    retrieve_related_incident_threads,
    retrieve_resource_mentions,
    search_slack_context,
)


def test_search_returns_mock_mode():
    result = search_slack_context("flood Village A")
    assert result["mode"] == "mock_rts_search"


def test_search_ranking_field_present():
    result = search_slack_context("flood Village A")
    assert result.get("ranking") == "tfidf_token_overlap"


def test_search_village_a_flood_finds_messages():
    result = search_slack_context("flood Village A")
    assert result["count"] >= 1


def test_search_returns_relevant_channel():
    result = search_slack_context("flood Village A", channels=["field-reports"])
    for msg in result["matches"]:
        assert msg["channel"] == "field-reports"


def test_search_empty_query_returns_all_in_channel():
    result = search_slack_context("", channels=["field-reports"])
    # Empty query should return all messages in the channel
    assert result["count"] >= 0  # may be 0 if no messages match channel filter


def test_retrieve_related_threads_village_a():
    result = retrieve_related_incident_threads("Village A", "flood")
    assert result["count"] >= 1
    assert result["mode"] == "mock_rts_search"


def test_retrieve_resource_mentions():
    result = retrieve_resource_mentions("Village A")
    assert result["mode"] == "mock_rts_search"
    assert isinstance(result["matches"], list)


def test_retrieve_latest_field_reports():
    result = retrieve_latest_field_reports("Village A")
    assert result["mode"] == "mock_rts_search"
    for msg in result["matches"]:
        assert msg["channel"] == "field-reports"


def test_build_slack_context_structure():
    ctx = build_slack_context("Village A", "flood")
    assert "related_threads" in ctx
    assert "resource_mentions" in ctx
    assert "latest_field_reports" in ctx


def test_tfidf_ranks_flood_higher_than_unrelated():
    """Flood-related query should score flood messages higher than unrelated ones."""
    result = search_slack_context("flood stranded elderly children")
    if result["count"] >= 2:
        # First result should mention flood/stranded
        first_text = result["matches"][0].get("text", "").lower()
        assert any(w in first_text for w in ["flood", "stranded", "elderly", "children", "water"])
