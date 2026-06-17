from langchain_core.prompts import ChatPromptTemplate


RESCUE_REASONING_PROMPT = ChatPromptTemplate.from_template("""
You are RescueNet AI's emergency reasoning layer.

Analyze the disaster mission context and produce a concise operational decision summary.

Location: {location}
Disaster Type: {disaster_type}
Severity: {severity}
Risk Level: {risk_level}
Incident Query: {query}

Resources:
{resources}

Routes:
{routes}

Hospitals:
{hospitals}

Return only:
1. Situation Summary
2. Immediate Priorities
3. Resource Decision
4. Safety Advisory
""")


def generate_langchain_decision_summary(state: dict) -> str:
    """
    LangChain-powered prompt orchestration layer.
    This enriches the final LangGraph mission output with structured reasoning.
    """

    prompt_value = RESCUE_REASONING_PROMPT.invoke({
        "location": state.get("location", "Unknown"),
        "disaster_type": state.get("disaster_type", "Unknown"),
        "severity": state.get("severity", "Unknown"),
        "risk_level": state.get("risk_level", "Unknown"),
        "query": state.get("query", ""),
        "resources": state.get("resources", {}),
        "routes": state.get("routes", {}),
        "hospitals": state.get("hospitals", []),
    })

    # No external LLM dependency needed for demo stability.
    # This still uses LangChain prompt orchestration and can later connect to Gemini/OpenAI.
    return prompt_value.to_string()
