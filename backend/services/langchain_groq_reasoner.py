import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


PROMPT = ChatPromptTemplate.from_template("""
You are RescueNet AI's emergency reasoning layer.

Generate a concise operational decision summary for disaster response.

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

Return in this format:
1. Situation Summary
2. Immediate Priorities
3. Resource Decision
4. Evacuation Guidance
5. Safety Advisory
""")


def get_groq_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )


def generate_groq_decision_summary(state: dict) -> str:
    try:
        chain = PROMPT | get_groq_llm()

        response = chain.invoke({
            "location": state.get("location", "Unknown"),
            "disaster_type": state.get("disaster_type", "Unknown"),
            "severity": state.get("severity", "Unknown"),
            "risk_level": state.get("risk_level", "Unknown"),
            "query": state.get("query", ""),
            "resources": state.get("resources", {}),
            "routes": state.get("routes", {}),
            "hospitals": state.get("hospitals", []),
        })

        return response.content

    except Exception as e:
        return (
            "Groq LangChain reasoning layer unavailable. "
            f"Fallback mission plan remains active. Error: {str(e)}"
        )
