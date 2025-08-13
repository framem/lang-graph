from langchain.tools import tool
import requests
from typing import Optional

"""
ReAct-Agenten erwarten typischerweise englische Labels und Tool-Namen, da LangChain intern darauf ausgelegt ist.
"""

@tool
def fetch_product(product_id: str) -> str:
    """Fetch product information by ID from the fake store API.

    Args:
        product_id: The product ID to fetch (1-20)

    Returns:
        Formatted product information as string
    """
    try:
        response = requests.get(f'https://fakestoreapi.com/products/{product_id}')
        if response.status_code == 200:
            product_data = response.json()
            return f"""
            Produkt (ID: {product_id}):
            - Name: {product_data.get('title', 'N/A')}
            - Preis: ${product_data.get('price', 'N/A')}
            - Kategorie: {product_data.get('category', 'N/A')}
            - Bewertung: {product_data.get('rating', {}).get('rate', 'N/A')}/5 ({product_data.get('rating', {}).get('count', 0)} Bewertungen)
            - Beschreibung: {product_data.get('description', 'N/A')}
            """.strip()
        else:
            return f"Produkt mit ID {product_id} nicht gefunden."
    except Exception as e:
        return f"Fehler beim Abrufen des Produkts: {str(e)}"

@tool
def search_products(category: Optional[str] = None) -> str:
    """Search for products, optionally filtered by category.

    Args:
        category: Optional category to filter by

    Returns:
        List of products as formatted string
    """
    try:
        url = 'https://fakestoreapi.com/products'
        response = requests.get(url)

        if response.status_code == 200:
            products = response.json()

            # Filter by category if provided
            if category:
                products = [product for product in products if product.get('category', '').lower() == category.lower()]

            if not products:
                if category:
                    return f"Keine Produkte in der Kategorie '{category}' gefunden."
                else:
                    return "Keine Produkte gefunden."

            result = "Gefundene Produkte:\n"
            for product in products:
                result += f"- ID {product['id']}: {product['title']} (${product['price']})\n"
            return result.strip()
        else:
            return "Fehler beim Suchen der Produkte."
    except Exception as e:
        return f"Fehler bei der Produktsuche: {str(e)}"


@tool
def get_product_categories() -> str:
    """Get all available product categories.

    Returns:
        List of available categories
    """
    try:
        response = requests.get('https://fakestoreapi.com/products')
        if response.status_code == 200:
            products = response.json()
            # Extrahiere eindeutige Kategorien aus allen Produkten
            categories = set()
            for product in products:
                category = product.get('category')
                if category:
                    categories.add(category)

            # Konvertiere zu sortierter Liste für konsistente Ausgabe
            unique_categories = sorted(categories)
            return f"Verfügbare Kategorien: {', '.join(unique_categories)}"
        else:
            return "Fehler beim Abrufen der Kategorien."
    except Exception as e:
        return f"Fehler beim Abrufen der Kategorien: {str(e)}"
