import json
import logging
from app.config import RECIPES_FILE


logger = logging.getLogger(__name__)

def load_recipes():
    """
    Loads recipes from the specified JSON file.
    """
    try:
        with open(RECIPES_FILE, encoding="utf-8") as f:
            recipes = json.load(f)
            logger.info(f"Recipes successfully loaded from {RECIPES_FILE}")
            return recipes
    except Exception as e:
        logger.error(f"Error loading recipes: {e}")
        return {}


def calculate_ingredients(summary: dict):
    """
    Returns a summary of required ingredients based on ordered dishes.
    """
    recipes = load_recipes()
    result = {}

    logger.info(f"Starting ingredient calculation for {len(summary)} dishes")

    for dish, count in summary.items():
        # Get the recipe for the dish
        recipe = recipes.get(dish, {})
        if not recipe:
            logger.warning(f"Recipe for dish '{dish}' not found")
        for ingredient, grams in recipe.items():
            # Accumulate the total amount needed for each ingredient
            result[ingredient] = result.get(ingredient, 0) + grams * count

    logger.info(f"Ingredient calculation completed: {len(result)} unique ingredients")

    return result
