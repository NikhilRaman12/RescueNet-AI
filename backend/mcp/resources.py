from typing import Dict, Any


class ResourceCatalog:
    """
    Operational resource catalog used by RescueNet AI.
    This layer represents structured emergency resources available to agents.
    """

    def __init__(self):
        self.inventory = {
            "food_packets": 500,
            "water_liters": 2000,
            "medical_kits": 80,
            "ambulances": 4,
            "rescue_boats": 6,
            "blankets": 300,
            "volunteers_available": 46,
            "shelter_beds": 230,
        }

    def get_inventory(self) -> Dict[str, Any]:
        return self.inventory

    def get_shortages(self) -> Dict[str, Any]:
        shortages = {}
        if self.inventory["medical_kits"] < 100:
            shortages["medical_kits"] = 100 - self.inventory["medical_kits"]
        if self.inventory["water_liters"] < 2500:
            shortages["water_liters"] = 2500 - self.inventory["water_liters"]
        return shortages

    def reserve(self, item: str, quantity: int) -> Dict[str, Any]:
        available = self.inventory.get(item, 0)

        if available < quantity:
            return {
                "item": item,
                "requested": quantity,
                "available": available,
                "reserved": 0,
                "status": "insufficient_stock",
            }

        self.inventory[item] = available - quantity
        return {
            "item": item,
            "requested": quantity,
            "reserved": quantity,
            "remaining": self.inventory[item],
            "status": "reserved",
        }


resource_catalog = ResourceCatalog()
