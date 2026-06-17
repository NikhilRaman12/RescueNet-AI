import random

__all__ = [
    "fetch_mosdac_data",
    "data_analysis_tool",
    "visualization_tool",
    "resource_allocation_tool",
    "volunteer_assignment_tool",
    "volunteer_communication_tool",
    "food_distribution_tool",
    "shelter_allocation_tool",
    "transportation_planning_tool",
    "alert_generation_tool",
    "plan_finalization_tool",
    "fetch_weather_tool",
    "fetch_healthcare_tool",
    "fetch_imd_tool",
    "fetch_all_external_data",
]

# -----------------------------
# SAFE STUBS (kept to avoid breakage)
# -----------------------------
def fetch_mosdac_data(*args, **kwargs):
    return {}

def data_analysis_tool(*args, **kwargs):
    return {}

def visualization_tool(*args, **kwargs):
    return {}

def resource_allocation_tool(*args, **kwargs):
    return {}

def volunteer_assignment_tool(*args, **kwargs):
    return {}

def volunteer_communication_tool(*args, **kwargs):
    return {}

def food_distribution_tool(*args, **kwargs):
    return {}

def shelter_allocation_tool(*args, **kwargs):
    return {}

def transportation_planning_tool(*args, **kwargs):
    return {}

def alert_generation_tool(*args, **kwargs):
    return {}

def plan_finalization_tool(*args, **kwargs):
    return {}

# -----------------------------
# REALTIME SIMULATION LAYER
# -----------------------------
def fetch_weather_tool(location):
    return {
        "location": location,
        "alert_level": random.choice(["yellow", "orange", "red"]),
        "rainfall_mm_24h": random.randint(80, 250),
        "wind_speed_kmph": random.randint(20, 80),
        "flood_likelihood": random.choice(["medium", "high"]),
        "confidence": round(random.uniform(0.75, 0.95), 2)
    }


def fetch_healthcare_tool(location):
    return {
        "location": location,
        "hospitals": [
            {
                "name": "Regional Emergency Hospital",
                "beds": random.randint(20, 50),
                "icu": random.randint(5, 15),
                "ambulances": random.randint(1, 5)
            },
            {
                "name": "Urban Medical Center",
                "beds": random.randint(15, 40),
                "icu": random.randint(3, 10),
                "ambulances": random.randint(1, 4)
            }
        ]
    }


def fetch_imd_tool(location):
    return {
        "location": location,
        "alert_level": random.choice(["yellow", "orange", "red"]),
        "risk": {
            "urban_flooding": random.choice(["medium", "high"]),
            "traffic": random.choice(["medium", "high"]),
        },
        "priority_zones": [
            "river belt",
            "low-lying areas",
            "transport corridors"
        ]
    }


def fetch_all_external_data(location):
    return {
        "weather": fetch_weather_tool(location),
        "imd": fetch_imd_tool(location),
        "healthcare": fetch_healthcare_tool(location)
    }
