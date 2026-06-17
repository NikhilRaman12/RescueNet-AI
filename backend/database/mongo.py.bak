from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


class OperationalDataStore:
    def __init__(self) -> None:
        self.locations = {
            "hyderabad": {
                "city": "Hyderabad",
                "state": "Telangana",
                "country": "India",
                "risk_profile": {
                    "urban_flooding": "high",
                    "traffic_congestion": "high",
                    "critical_infrastructure_density": "high",
                    "heat_stress": "medium",
                },
                "priority_zones": [
                    "Musi River belt",
                    "low-lying residential clusters",
                    "hospital access roads",
                    "major transport corridors",
                ],
            },
            "vijayawada": {
                "city": "Vijayawada",
                "state": "Andhra Pradesh",
                "country": "India",
                "risk_profile": {
                    "river_flooding": "high",
                    "urban_congestion": "medium",
                    "cyclone_rainfall": "medium",
                },
                "priority_zones": [
                    "Krishna riverbank settlements",
                    "railway station access zone",
                    "low-lying colonies",
                ],
            },
            "chennai": {
                "city": "Chennai",
                "state": "Tamil Nadu",
                "country": "India",
                "risk_profile": {
                    "cyclone": "high",
                    "coastal_flooding": "high",
                    "urban_flooding": "high",
                },
                "priority_zones": [
                    "coastal settlements",
                    "Adyar river belt",
                    "Buckingham canal belt",
                    "subway and underpass zones",
                ],
            },
        }

        self.weather_alerts = {
            "hyderabad": {
                "alert_level": "orange",
                "condition": "heavy_rain_watch",
                "rainfall_mm_24h": 96,
                "wind_speed_kmph": 42,
                "flood_likelihood": "high",
                "confidence": 0.84,
                "recommended_monitoring_minutes": 30,
            },
            "vijayawada": {
                "alert_level": "orange",
                "condition": "river_rise_watch",
                "rainfall_mm_24h": 110,
                "wind_speed_kmph": 36,
                "flood_likelihood": "high",
                "confidence": 0.82,
                "recommended_monitoring_minutes": 30,
            },
            "chennai": {
                "alert_level": "red",
                "condition": "coastal_heavy_rain_warning",
                "rainfall_mm_24h": 145,
                "wind_speed_kmph": 58,
                "flood_likelihood": "very_high",
                "confidence": 0.88,
                "recommended_monitoring_minutes": 15,
            },
        }

        self.shelters = {
            "hyderabad": [
                {"shelter_id": "HYD-SH-001", "name": "Emergency Relief Camp A", "zone": "central", "capacity": 250, "available_beds": 120, "has_medical_support": True, "has_drinking_water": True, "has_power_backup": True},
                {"shelter_id": "HYD-SH-002", "name": "Community Shelter B", "zone": "west", "capacity": 180, "available_beds": 80, "has_medical_support": False, "has_drinking_water": True, "has_power_backup": True},
                {"shelter_id": "HYD-SH-003", "name": "Medical Stabilization Center", "zone": "east", "capacity": 75, "available_beds": 30, "has_medical_support": True, "has_drinking_water": True, "has_power_backup": True},
            ],
            "vijayawada": [
                {"shelter_id": "VJA-SH-001", "name": "Municipal Relief Center", "zone": "riverbank", "capacity": 220, "available_beds": 95, "has_medical_support": True, "has_drinking_water": True, "has_power_backup": True},
                {"shelter_id": "VJA-SH-002", "name": "Government School Relief Camp", "zone": "north", "capacity": 300, "available_beds": 160, "has_medical_support": False, "has_drinking_water": True, "has_power_backup": False},
            ],
            "chennai": [
                {"shelter_id": "CHN-SH-001", "name": "Coastal Emergency Shelter", "zone": "south_coastal", "capacity": 400, "available_beds": 210, "has_medical_support": True, "has_drinking_water": True, "has_power_backup": True},
                {"shelter_id": "CHN-SH-002", "name": "Urban Flood Relief School", "zone": "central", "capacity": 320, "available_beds": 140, "has_medical_support": True, "has_drinking_water": True, "has_power_backup": False},
            ],
        }

        self.resource_inventory = {
            "hyderabad": {"food_packets": 500, "water_liters": 2000, "medical_kits": 80, "ambulances": 4, "rescue_boats": 6, "blankets": 300, "portable_lights": 45, "power_banks": 120, "volunteers_available": 46},
            "vijayawada": {"food_packets": 650, "water_liters": 2600, "medical_kits": 100, "ambulances": 5, "rescue_boats": 9, "blankets": 380, "portable_lights": 55, "power_banks": 150, "volunteers_available": 58},
            "chennai": {"food_packets": 900, "water_liters": 4200, "medical_kits": 140, "ambulances": 8, "rescue_boats": 14, "blankets": 600, "portable_lights": 85, "power_banks": 220, "volunteers_available": 82},
        }

        self.hospitals = {
            "hyderabad": [
                {"hospital_id": "HYD-HSP-001", "name": "Regional Emergency Hospital", "emergency_beds_available": 30, "icu_beds_available": 8, "ambulances_available": 3, "trauma_ready": True},
                {"hospital_id": "HYD-HSP-002", "name": "Urban Medical Response Center", "emergency_beds_available": 22, "icu_beds_available": 5, "ambulances_available": 2, "trauma_ready": True},
            ],
            "vijayawada": [
                {"hospital_id": "VJA-HSP-001", "name": "River Zone Emergency Hospital", "emergency_beds_available": 26, "icu_beds_available": 6, "ambulances_available": 3, "trauma_ready": True},
            ],
            "chennai": [
                {"hospital_id": "CHN-HSP-001", "name": "Coastal Disaster Medical Center", "emergency_beds_available": 48, "icu_beds_available": 12, "ambulances_available": 6, "trauma_ready": True},
            ],
        }

        self.routes = {
            "hyderabad": {"recommended_route": "Route A", "backup_route": "Route B", "blocked_routes": ["Low-lying river road", "Old bridge access road"], "routing_strategy": "avoid_flooded_or_congested_segments", "estimated_evacuation_minutes": 42},
            "vijayawada": {"recommended_route": "Riverbank bypass corridor", "backup_route": "Northern municipal road", "blocked_routes": ["Krishna river service road"], "routing_strategy": "avoid_riverbank_overflow_zones", "estimated_evacuation_minutes": 38},
            "chennai": {"recommended_route": "High-ground arterial route", "backup_route": "Inner ring diversion", "blocked_routes": ["Coastal road section", "low subway underpass"], "routing_strategy": "avoid_coastal_surge_and_underpass_segments", "estimated_evacuation_minutes": 55},
        }

        self.volunteer_units = {
            "hyderabad": {"medical": 12, "rescue": 18, "logistics": 10, "communications": 6, "shelter_support": 8},
            "vijayawada": {"medical": 10, "rescue": 22, "logistics": 12, "communications": 5, "shelter_support": 9},
            "chennai": {"medical": 18, "rescue": 30, "logistics": 18, "communications": 10, "shelter_support": 16},
        }

        self.incidents: List[Dict[str, Any]] = []

    def _key(self, location: str) -> str:
        key = (location or "hyderabad").strip().lower()
        return key if key in self.locations else "hyderabad"

    def get_location_profile(self, location: str) -> Dict[str, Any]:
        return self.locations[self._key(location)]

    def get_weather_alert(self, location: str) -> Dict[str, Any]:
        return self.weather_alerts[self._key(location)]

    def get_shelters(self, location: str) -> List[Dict[str, Any]]:
        return self.shelters[self._key(location)]

    def get_resource_inventory(self, location: str) -> Dict[str, Any]:
        return self.resource_inventory[self._key(location)]

    def get_hospitals(self, location: str) -> List[Dict[str, Any]]:
        return self.hospitals[self._key(location)]

    def get_routes(self, location: str) -> Dict[str, Any]:
        return self.routes[self._key(location)]

    def get_volunteer_units(self, location: str) -> Dict[str, Any]:
        return self.volunteer_units[self._key(location)]

    def get_operational_snapshot(self, location: str) -> Dict[str, Any]:
        key = self._key(location)
        return {
            "snapshot_id": str(uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "location_profile": self.locations[key],
            "weather_alert": self.weather_alerts[key],
            "shelters": self.shelters[key],
            "resource_inventory": self.resource_inventory[key],
            "hospitals": self.hospitals[key],
            "routes": self.routes[key],
            "volunteer_units": self.volunteer_units[key],
        }

    def record_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        stored = {
            "incident_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            **incident,
        }
        self.incidents.append(stored)
        return stored

    def list_incidents(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.incidents[-limit:]


operational_store = OperationalDataStore()


def get_database() -> OperationalDataStore:
    return operational_store


def get_operational_snapshot(location: str = "Hyderabad") -> Dict[str, Any]:
    return operational_store.get_operational_snapshot(location)


def record_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    return operational_store.record_incident(incident)


def list_incidents(limit: int = 20) -> List[Dict[str, Any]]:
    return operational_store.list_incidents(limit)
