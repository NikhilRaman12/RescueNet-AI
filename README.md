# RescueNet AI

## Autonomous Multi-Agent Disaster Response Command System

RescueNet AI is an AI-powered disaster response platform that coordinates emergency rescue missions using FastAPI, LangChain, LangGraph StateGraph, MCP tools, A2A communication, and live public intelligence APIs.

## Core Stack

- FastAPI backend
- LangChain reasoning layer
- LangGraph StateGraph orchestration
- MCP operational tools
- A2A agent communication
- Real-time dashboard
- Live API integrations

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

## Live Data Sources

- Open-Meteo Weather API
- NASA EONET Disaster Events
- USGS Earthquake Feed
- OpenStreetMap Geocoding
- OSRM Routing API

## Features

- Real-time disaster intelligence
- Multi-agent emergency planning
- A2A handoff messages
- Live weather, routing, geocoding, disaster, and earthquake data
- Shelter, hospital, route, resource, and volunteer planning
- Public alert generation
- Interactive emergency operations dashboard

## Main API Endpoints

```text
GET  /
GET  /console
GET  /health
POST /api/rescue
GET  /api/live/data
GET  /api/mcp/context
GET  /api/a2a/messages
GET  /api/dashboard
cd "/workspace/tcs-amd-ai-hackathon-nikhil_Raman/RescueNet-AI"

cat > README.md <<'EOF'
# 🚨 RescueNet AI

## Autonomous Multi-Agent Disaster Response Command System

RescueNet AI is an enterprise-grade AI-powered disaster response platform designed to assist emergency management teams during floods, cyclones, earthquakes, wildfires, landslides, and other large-scale emergencies.

The system leverages autonomous AI agents, real-time operational intelligence, live public APIs, and coordinated multi-agent workflows to transform fragmented disaster information into actionable rescue plans.

---

# 🌟 Key Highlights

✅ Multi-Agent Disaster Intelligence Platform

✅ LangGraph StateGraph Orchestration

✅ LangChain Agent Framework

✅ MCP (Model Context Protocol) Integration

✅ A2A (Agent-to-Agent) Communication

✅ FastAPI Backend Services

✅ Real-Time Operational Dashboard

✅ Live Public Intelligence APIs

✅ Emergency Planning & Resource Coordination

---

# 🏗 System Architecture

Frontend Dashboard
↓
FastAPI Backend
↓
LangGraph StateGraph
↓
Multi-Agent Workflow
↓
MCP Operational Tools
↓
A2A Communication Layer
↓
Mission Planning Engine
↓
Emergency Response Recommendations

---

# 🤖 Specialized AI Agents

### 1. Disaster Intelligence Agent
Analyzes disaster type, severity, and risk factors.

### 2. Priority Scoring Agent
Calculates mission priority and response urgency.

### 3. Damage Assessment Agent
Evaluates potential infrastructure and population impact.

### 4. Shelter Coordination Agent
Identifies shelters and evacuation facilities.

### 5. Route Optimization Agent
Generates evacuation and logistics routes.

### 6. Resource Allocation Agent
Plans distribution of emergency resources.

### 7. Medical Triage Agent
Coordinates medical response strategies.

### 8. Volunteer Coordination Agent
Assigns volunteer resources and support teams.

### 9. Public Alert Agent
Generates public emergency notifications.

### 10. Mission Planner Agent
Produces final coordinated rescue mission plans.

---

# 🔄 Agent-to-Agent (A2A) Workflow

Disaster Agent
→ Priority Agent
→ Damage Agent
→ Shelter Agent
→ Route Agent
→ Resource Agent
→ Medical Agent
→ Volunteer Agent
→ Alert Agent
→ Mission Planner

Each agent receives context from previous agents and contributes specialized intelligence before handing off to the next agent.

---

# 🧠 LangGraph StateGraph

RescueNet AI uses LangGraph StateGraph to manage:

- Shared mission state
- Agent execution flow
- Agent coordination
- Context propagation
- Multi-step reasoning
- Mission planning lifecycle

---

# 🔌 MCP Tool Integration

RescueNet AI integrates external operational tools using MCP-style service architecture.

Supported capabilities:

- Weather Intelligence
- Disaster Monitoring
- Geospatial Intelligence
- Route Optimization
- Emergency Context Retrieval

---

# 🌍 Live Data Sources

## Open-Meteo API

Provides:

- Temperature
- Humidity
- Rainfall
- Wind Speed
- Weather Conditions

## NASA EONET API

Provides:

- Active Disaster Events
- Wildfires
- Storm Events
- Environmental Hazards

## USGS Earthquake API

Provides:

- Recent Earthquakes
- Magnitude Information
- Event Locations

## OpenStreetMap Nominatim

Provides:

- Geocoding
- Location Resolution
- Geographic Context

## OSRM Routing API

Provides:

- Route Planning
- Travel Distance
- Estimated Travel Time
- Evacuation Routing

---

# 📊 Dashboard Features

### Emergency Operations Console

Displays:

- System Status
- Active Missions
- Operational Intelligence
- Live Weather
- Disaster Events
- Earthquake Monitoring
- Geospatial Data
- Routing Information
- A2A Communications
- Mission Response Plans

---

# 🚑 Operational Capabilities

### Disaster Assessment

- Flood Risk Evaluation
- Earthquake Monitoring
- Cyclone Tracking
- Wildfire Awareness

### Resource Planning

- Ambulances
- Medical Kits
- Rescue Boats
- Emergency Supplies
- Volunteer Teams

### Emergency Coordination

- Shelter Assignment
- Route Planning
- Medical Response
- Public Safety Alerts

---

# 📡 API Endpoints

## System

GET /

GET /health

GET /console

---

## Rescue Operations

POST /api/rescue

---

## MCP Services

GET /api/mcp/context

GET /api/mcp/events

GET /api/mcp/server

---

## Live Data

GET /api/live/data

---

## Dashboard

GET /api/dashboard

GET /api/data/snapshot

GET /api/data/incidents

---

## A2A Communication

GET /api/a2a/messages

GET /api/a2a/conversation/{correlation_id}

---

# 🚀 Example Mission Request

curl -X POST "http://127.0.0.1:8030/api/rescue" \
-H "Content-Type: application/json" \
-d '{
  "location":"Hyderabad",
  "disaster_type":"Flood",
  "severity":"High",
  "query":"Flood alert near river zone. People are trapped and injured. Evacuation is needed."
}'

---

# 📈 Mission Output

RescueNet AI generates:

- Disaster Analysis
- Priority Assessment
- Damage Evaluation
- Shelter Recommendations
- Route Plans
- Resource Allocation
- Medical Response Plans
- Volunteer Coordination
- Public Alerts
- Final Rescue Mission Plan

---

# 🛠 Technology Stack

### Backend

- Python
- FastAPI
- Pydantic

### Agentic AI

- LangChain
- LangGraph StateGraph

### Communication

- A2A Protocol

### Operational Intelligence

- MCP Services

### APIs

- Open-Meteo
- NASA EONET
- USGS
- OpenStreetMap
- OSRM

### Frontend

- HTML
- CSS
- JavaScript

---

# 🎯 Innovation

RescueNet AI demonstrates how autonomous AI agents can collaborate using LangGraph workflows, MCP operational tools, A2A communication, and real-time intelligence APIs to support disaster response decision-making.

The platform combines live operational intelligence with coordinated agent reasoning to generate actionable rescue strategies for emergency scenarios.

---

# 🏆 AMD AI Hackathon 2026

Built as a real-world Agentic AI solution showcasing:

- Multi-Agent Systems
- LangGraph Orchestration
- MCP Integration
- A2A Communication
- Real-Time Operational Intelligence
- Disaster Response Automation

RescueNet AI — Turning Live Intelligence into Coordinated Emergency Action.
