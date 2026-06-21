"""Nutrition data helpers.

Pulls real, reliable nutrition facts from free public sources instead of
scraping random websites:

- USDA FoodData Central  (official US government nutrition database)
- Open Food Facts        (open database of packaged/branded products)

These are proper APIs, so they are far more stable and ethical than scraping.
"""

import os
import requests

USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

# Nutrients we care about, keyed by USDA nutrient name.
_KEY_NUTRIENTS = {
    "Energy": "calories",
    "Protein": "protein_g",
    "Total lipid (fat)": "fat_g",
    "Carbohydrate, by difference": "carbs_g",
    "Fiber, total dietary": "fiber_g",
    "Sugars, total including NLEA": "sugar_g",
}


def lookup_usda(query: str, max_results: int = 3) -> list[dict]:
    """Search USDA FoodData Central for a food and return key nutrients per 100g."""
    params = {
        "query": query,
        "pageSize": max_results,
        "api_key": USDA_API_KEY,
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
    }
    try:
        resp = requests.get(USDA_SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        foods = resp.json().get("foods", [])
    except requests.RequestException as exc:
        return [{"error": f"USDA lookup failed: {exc}"}]

    results = []
    for food in foods:
        item = {"name": food.get("description", "Unknown"), "source": "USDA"}
        for nutrient in food.get("foodNutrients", []):
            label = nutrient.get("nutrientName")
            if label in _KEY_NUTRIENTS:
                item[_KEY_NUTRIENTS[label]] = nutrient.get("value")
        results.append(item)
    return results


def lookup_openfoodfacts(query: str, max_results: int = 3) -> list[dict]:
    """Search Open Food Facts for branded products (per 100g)."""
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": max_results,
    }
    try:
        resp = requests.get(OFF_SEARCH_URL, params=params, timeout=15,
                            headers={"User-Agent": "FitnessNutritionChatbot/1.0"})
        resp.raise_for_status()
        products = resp.json().get("products", [])
    except requests.RequestException as exc:
        return [{"error": f"Open Food Facts lookup failed: {exc}"}]

    results = []
    for prod in products:
        n = prod.get("nutriments", {})
        results.append({
            "name": prod.get("product_name") or "Unknown product",
            "source": "Open Food Facts",
            "calories": n.get("energy-kcal_100g"),
            "protein_g": n.get("proteins_100g"),
            "fat_g": n.get("fat_100g"),
            "carbs_g": n.get("carbohydrates_100g"),
            "fiber_g": n.get("fiber_100g"),
            "sugar_g": n.get("sugars_100g"),
        })
    return results


def get_nutrition_facts(query: str) -> str:
    """Return a compact, human-readable nutrition summary for a food query.

    This string is fed to the LLM as grounding context so answers use real
    numbers rather than guesses.
    """
    items = lookup_usda(query) or []
    if not items or items[0].get("error"):
        items = lookup_openfoodfacts(query)

    if not items or items[0].get("error"):
        return f"No reliable nutrition data found for '{query}'."

    lines = [f"Nutrition data for '{query}' (per 100 g):"]
    for it in items:
        if it.get("error"):
            continue
        lines.append(
            f"- {it['name']} [{it['source']}]: "
            f"{it.get('calories', '?')} kcal, "
            f"protein {it.get('protein_g', '?')} g, "
            f"carbs {it.get('carbs_g', '?')} g, "
            f"fat {it.get('fat_g', '?')} g, "
            f"fiber {it.get('fiber_g', '?')} g, "
            f"sugar {it.get('sugar_g', '?')} g"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick manual test: python nutrition.py
    print(get_nutrition_facts("banana"))
