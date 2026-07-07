from backend.evaluation.evaluator import evaluate_response


def test_evaluation_summary():
    state = {
        "disaster_analysis": {"risk": "high"},
        "priority_score": {"score": 90},
        "damage_assessment": {"damage": "high"},
        "public_alert": {"message": "alert"},
        "recommended_actions": ["evacuate"],
        "final_mission_plan": {"plan": "go"},
        "live_data_sources": {"weather": {"status": "live"}},
        "a2a_trace": ["a", "b", "c"],
        "guardrail_report": {"passed": True},
        "mission_id": "m1",
        "correlation_id": "c1",
        "status": "completed",
        "agents_used": ["A"],
        "agent_outputs": {"A": {"ok": True}},
    }
    report = evaluate_response(state)
    assert report["final_score"] >= 0
    assert "scores" in report
