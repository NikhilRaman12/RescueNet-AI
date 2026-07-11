from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple
import requests


CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "hyderabad": (17.3850, 78.4867),
    "vijayawada": (16.5062, 80.6480),
    "chennai": (13.0827, 80.2707),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "kolkata": (22.5726, 88.3639),
    "bengaluru": (12.9716, 77.5946),
    "visakhapatnam": (17.6868, 83.2185),
    "bhubaneswar": (20.2961, 85.8245),
    "guwahati": (26.1445, 91.7362),
}


def _city_key(location: str) -> str:
    return (location or "hyderabad").strip().lower()


def _coords(location: str) -> Tuple[float, float]:
    return CITY_COORDS.get(_city_key(location), CITY_COORDS["hyderabad"])


def live_weather_tool(location: str) -> Dict[str, Any]:
    lat, lon = _coords(location)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m"
    )

    try:
        r = requests.get(url, timeout=3)
        r.raise_for_status()
        current = r.json().get("current", {})

        return {
            "tool": "open_meteo_live_weather",
            "source": "Open-Meteo API",
            "status": "live",
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": current.get("temperature_2m"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "rain_mm": current.get("rain"),
            "wind_speed_kmph": current.get("wind_speed_10m"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "tool": "open_meteo_live_weather",
            "source": "Open-Meteo API",
            "status": "fallback",
            "location": location,
            "error": str(e),
        }


def live_disaster_events_tool(location: str) -> Dict[str, Any]:
    try:
        url = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=10"
        r = requests.get(url, timeout=3)
        r.raise_for_status()
        events = r.json().get("events", [])

        simplified = []
        for event in events[:10]:
            simplified.append({
                "id": event.get("id"),
                "title": event.get("title"),
                "categories": [c.get("title") for c in event.get("categories", [])],
                "source": "NASA EONET",
            })

        return {
            "tool": "nasa_eonet_disaster_events",
            "source": "NASA EONET API",
            "status": "live",
            "location_reference": location,
            "open_events_count": len(events),
            "events": simplified,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "tool": "nasa_eonet_disaster_events",
            "source": "NASA EONET API",
            "status": "fallback",
            "location_reference": location,
            "error": str(e),
        }


def live_earthquake_tool(location: str) -> Dict[str, Any]:
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson"
        r = requests.get(url, timeout=3)
        r.raise_for_status()
        features = r.json().get("features", [])

        quakes = []
        for f in features[:10]:
            props = f.get("properties", {})
            geom = f.get("geometry", {})
            quakes.append({
                "place": props.get("place"),
                "magnitude": props.get("mag"),
                "time": props.get("time"),
                "coordinates": geom.get("coordinates"),
                "source": "USGS",
            })

        return {
            "tool": "usgs_earthquake_feed",
            "source": "USGS Earthquake API",
            "status": "live",
            "location_reference": location,
            "significant_events_count": len(features),
            "events": quakes,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "tool": "usgs_earthquake_feed",
            "source": "USGS Earthquake API",
            "status": "fallback",
            "location_reference": location,
            "error": str(e),
        }


def live_geocode_tool(location: str) -> Dict[str, Any]:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": f"{location}, India", "format": "json", "limit": 1}
        headers = {"User-Agent": "RescueNetAI-Hackathon/1.0"}

        r = requests.get(url, params=params, headers=headers, timeout=3)
        r.raise_for_status()
        data = r.json()

        if not data:
            lat, lon = _coords(location)
            return {
                "tool": "openstreetmap_geocode",
                "source": "OpenStreetMap Nominatim",
                "status": "fallback",
                "location": location,
                "latitude": lat,
                "longitude": lon,
                "reason": "No geocoding result; used local coordinate profile.",
            }

        item = data[0]
        return {
            "tool": "openstreetmap_geocode",
            "source": "OpenStreetMap Nominatim",
            "status": "live",
            "location": location,
            "display_name": item.get("display_name"),
            "latitude": float(item.get("lat")),
            "longitude": float(item.get("lon")),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        lat, lon = _coords(location)
        return {
            "tool": "openstreetmap_geocode",
            "source": "OpenStreetMap Nominatim",
            "status": "fallback",
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "error": str(e),
        }


def live_routing_tool(location: str) -> Dict[str, Any]:
    lat, lon = _coords(location)

    # Demo route: nearby point offset to simulate evacuation movement.
    start_lon, start_lat = lon, lat
    end_lon, end_lat = lon + 0.05, lat + 0.05

    try:
        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}"
            "?overview=false&alternatives=true&steps=false"
        )

        r = requests.get(url, timeout=3)
        r.raise_for_status()
        data = r.json()
        routes = data.get("routes", [])

        if not routes:
            raise RuntimeError("No OSRM route returned")

        best = routes[0]
        return {
            "tool": "osrm_live_routing",
            "source": "OSRM Public Routing API",
            "status": "live",
            "location": location,
            "start": {"lat": start_lat, "lon": start_lon},
            "end": {"lat": end_lat, "lon": end_lon},
            "distance_km": round(best.get("distance", 0) / 1000, 2),
            "duration_minutes": round(best.get("duration", 0) / 60, 2),
            "routes_returned": len(routes),
            "routing_strategy": "live_public_osrm_route_estimation",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "tool": "osrm_live_routing",
            "source": "OSRM Public Routing API",
            "status": "fallback",
            "location": location,
            "error": str(e),
        }


def fetch_live_data_bundle(location: str) -> Dict[str, Any]:
    return {
        "live_weather": live_weather_tool(location),
        "live_disaster_events": live_disaster_events_tool(location),
        "live_earthquakes": live_earthquake_tool(location),
        "live_geocoding": live_geocode_tool(location),
        "live_routing": live_routing_tool(location),
    }
