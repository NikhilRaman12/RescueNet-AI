# RescueNet AI

## Autonomous Disaster Response Command System

RescueNet AI is an agentic disaster response platform that helps emergency teams assess incidents, coordinate resources, optimize routes, manage shelters, support medical triage, and generate actionable rescue plans through intelligent multi-agent collaboration.

Built for AMD AI Hackathon 2026.

---

## Problem

Disaster response operations often suffer from:

- Delayed decision-making
- Fragmented situational awareness
- Inefficient resource allocation
- Poor coordination between response teams
- Lack of real-time operational intelligence

RescueNet AI addresses these challenges through a coordinated multi-agent emergency response framework.

---

## Solution

RescueNet AI transforms disaster information into coordinated rescue missions using:

- Multi-Agent Intelligence
- LangGraph StateGraph Orchestration
- LangChain Reasoning Layer
- MCP Operational Context
- A2A Agent Communication
- FastAPI Backend Services
- Real-Time Emergency Dashboard

---

## Key Features

### Disaster Intelligence
Analyzes incoming disaster events and assesses overall risk.

### Priority Scoring
Determines incident severity and response urgency.

### Damage Assessment
Estimates impact on people, infrastructure, and resources.

### Shelter Coordination
Identifies and allocates available shelters.

### Route Optimization
Generates primary and backup evacuation routes.

### Resource Allocation
Allocates emergency supplies and rescue assets.

### Medical Triage
Evaluates healthcare capacity and emergency readiness.

### Volunteer Coordination
Deploys available volunteer resources.

### Public Alert System
Generates emergency notifications and advisories.

### Mission Planning
Creates a complete rescue response strategy.

---

## System Architecture

User Request
        │
        ▼
Emergency Operations Console
        │
        ▼
FastAPI Backend
        │
        ▼
LangGraph StateGraph
        │
        ▼
10 Specialized AI Agents
        │
        ▼
MCP Operational Context
        │
        ▼
A2A Agent Communication
        │
        ▼
Mission Planning Engine
        │
        ▼
Rescue Response Plan

---

## Technology Stack

### Backend
- Python
- FastAPI

### Agentic AI
- LangChain
- LangGraph StateGraph
- State-Based Workflows

### Communication
- A2A Protocol

### Operational Context
- MCP (Model Context Protocol)

### Data Layer
- Operational Data Store
- MongoDB

### Frontend
- HTML
- CSS
- JavaScript

---

## Agent Network

1. Disaster Intelligence Agent
2. Priority Scoring Agent
3. Damage Assessment Agent
4. Shelter Coordination Agent
5. Route Optimization Agent
6. Resource Allocation Agent
7. Medical Triage Agent
8. Volunteer Coordination Agent
9. Public Alert Agent
10. Mission Planner Agent

---

## MCP Operational Context

RescueNet AI integrates operational context including:

- Weather Alerts
- Disaster Warnings
- Hospital Capacity
- Shelter Availability
- Resource Inventory
- Route Intelligence
- Volunteer Availability
- Public Safety Information

---

## A2A Communication

Agents collaborate through structured A2A communication:

- Agent Handoffs
- State Preservation
- Context Sharing
- Traceability
- Correlation Tracking
- Multi-Agent Coordination

---

## Example Mission

Location: Hyderabad

Disaster Type: Flood

Severity: High

Incident:

"Flood alert near river zone. People are trapped and injured. Evacuation is needed."

Generated Outputs:

- Risk Assessment
- Shelter Plan
- Route Plan
- Resource Allocation
- Hospital Capacity Analysis
- Volunteer Deployment
- Public Alert
- Complete Rescue Mission Plan

---

## Dashboard Capabilities

- Incident Monitoring
- Resource Tracking
- Hospital Availability
- Route Intelligence
- MCP Operational Context
- A2A Communication Logs
- Full Mission Payload
- Real-Time Decision Support

---

## Project Impact

RescueNet AI enables:

- Faster Emergency Response
- Better Resource Utilization
- Improved Coordination
- Reduced Response Delays
- State-Aware Agent Collaboration
- Scalable Disaster Management

---

## Run Locally

```bash
pip install -r requirements.txt

uvicorn backend.main:app --host 0.0.0.0 --port 8030
```

Open:

http://localhost:8030/console

---

## Repository Structure

RescueNet-AI/

├── backend/

│   ├── agents/

│   ├── services/

│   ├── mcp/

│   ├── a2a/

│   ├── routers/

│   ├── schemas/

│   └── database/

│

├── frontend/

├── frontend_static/

├── src/

└── README.md

---

## Future Enhancements

- Live Weather APIs
- GIS Integration
- Satellite Intelligence
- Real Hospital APIs
- Government Disaster Feeds
- Mobile Emergency Interface
- Multi-City Deployments

---

## AMD AI Hackathon 2026

RescueNet AI demonstrates how Agentic AI can transform disaster response by combining multi-agent reasoning, operational context, and coordinated decision intelligence into a unified emergency command system.

Developed by Nikhil Raman K.
