"""
Pizza catalog and matching service.
Handles all pizza-related business logic including search, matching, and inventory.
"""

from typing import List, Optional, Dict, Set
from dataclasses import dataclass
from state import Pizza

@dataclass
class PizzaMatchResult:
    """Result of pizza matching operation"""
    matches: List[Pizza]
    confidence_score: float
    search_terms: List[str]
    fuzzy_matches: List[Pizza] = None

class PizzaCatalogService:
    """Service for managing pizza catalog and search operations"""
    
    def __init__(self):
        self._catalog = self._initialize_catalog()
        self._ingredient_index = self._build_ingredient_index()
    
    def _initialize_catalog(self) -> Dict[str, Pizza]:
        """Initialize the pizza catalog with available pizzas"""
        pizzas = {
            'margherita': Pizza(
                name='margherita',
                description='Classic Margherita with fresh basil',
                ingredients=['tomato', 'mozzarella', 'basil', 'olive oil'],
                price=12.99
            ),
            'pepperoni': Pizza(
                name='pepperoni',
                description='Classic Pepperoni with spicy pepperoni slices',
                ingredients=['tomato', 'mozzarella', 'pepperoni'],
                price=14.99
            ),
            'hawaiian': Pizza(
                name='hawaiian',
                description='Hawaiian with ham and pineapple',
                ingredients=['tomato', 'mozzarella', 'ham', 'pineapple'],
                price=15.99
            ),
            'veggie': Pizza(
                name='veggie supreme',
                description='Veggie Supreme with fresh vegetables',
                ingredients=['tomato', 'mozzarella', 'peppers', 'mushrooms', 'onions', 'olives'],
                price=13.99
            ),
            'meat_lovers': Pizza(
                name='meat lovers',
                description='Meat Lovers with multiple meat toppings',
                ingredients=['tomato', 'mozzarella', 'pepperoni', 'sausage', 'bacon', 'ham'],
                price=17.99
            ),
            'bbq_chicken': Pizza(
                name='bbq chicken',
                description='BBQ Chicken with tangy BBQ sauce',
                ingredients=['bbq sauce', 'mozzarella', 'chicken', 'onions', 'cilantro'],
                price=16.99
            )
        }
        return pizzas
    
    def _build_ingredient_index(self) -> Dict[str, Set[str]]:
        """Build an index mapping ingredients to pizza names for faster search"""
        index = {}
        for pizza_name, pizza in self._catalog.items():
            for ingredient in pizza.ingredients:
                if ingredient not in index:
                    index[ingredient] = set()
                index[ingredient].add(pizza_name)
        return index
    
    def get_all_pizzas(self) -> List[Pizza]:
        """Get all available pizzas"""
        return list(self._catalog.values())
    
    def get_pizza_by_name(self, name: str) -> Optional[Pizza]:
        """Get a specific pizza by name"""
        return self._catalog.get(name.lower().replace(' ', '_'))
    
    def search_pizzas(self, query: str, max_results: int = 5) -> PizzaMatchResult:
        """
        Search for pizzas based on user query with improved matching logic
        
        Args:
            query: User's pizza request
            max_results: Maximum number of results to return
            
        Returns:
            PizzaMatchResult with matched pizzas and confidence scores
        """
        query_lower = query.lower()
        search_terms = self._extract_search_terms(query_lower)
        
        # Direct name matches (highest priority)
        direct_matches = self._find_direct_matches(search_terms)
        
        # Ingredient matches (medium priority) 
        ingredient_matches = self._find_ingredient_matches(search_terms)
        
        # Fuzzy matches (lowest priority)
        fuzzy_matches = self._find_fuzzy_matches(search_terms)
        
        # Combine and rank results
        all_matches = self._rank_matches(direct_matches, ingredient_matches, fuzzy_matches)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(query_lower, all_matches[:max_results])
        
        return PizzaMatchResult(
            matches=all_matches[:max_results],
            confidence_score=confidence,
            search_terms=search_terms,
            fuzzy_matches=fuzzy_matches if fuzzy_matches else None
        )
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from user query"""
        # Remove common stopwords and pizza-related terms
        stopwords = {'i', 'want', 'like', 'get', 'order', 'pizza', 'please', 'can', 'have', 'a', 'an', 'the'}
        terms = [term.strip() for term in query.split() if term.strip() not in stopwords and len(term.strip()) > 2]
        return terms
    
    def _find_direct_matches(self, search_terms: List[str]) -> List[tuple[Pizza, float]]:
        """Find pizzas with direct name matches"""
        matches = []
        for term in search_terms:
            for pizza_name, pizza in self._catalog.items():
                # Check if search term matches pizza name
                if term in pizza_name or pizza_name.replace('_', ' ') in ' '.join(search_terms):
                    matches.append((pizza, 1.0))  # Perfect match
        return matches
    
    def _find_ingredient_matches(self, search_terms: List[str]) -> List[tuple[Pizza, float]]:
        """Find pizzas based on ingredient matches"""
        ingredient_scores = {}
        
        for term in search_terms:
            for ingredient, pizza_names in self._ingredient_index.items():
                if term in ingredient or ingredient in term:
                    for pizza_name in pizza_names:
                        pizza = self._catalog[pizza_name]
                        if pizza not in ingredient_scores:
                            ingredient_scores[pizza] = 0
                        ingredient_scores[pizza] += 0.7  # Ingredient match score
        
        return [(pizza, score) for pizza, score in ingredient_scores.items()]
    
    def _find_fuzzy_matches(self, search_terms: List[str]) -> List[tuple[Pizza, float]]:
        """Find pizzas using fuzzy string matching"""
        fuzzy_matches = []
        
        for term in search_terms:
            for pizza_name, pizza in self._catalog.items():
                # Simple fuzzy matching - check if term is substring
                if len(term) >= 3:
                    if term in pizza_name or term in pizza.description.lower():
                        fuzzy_matches.append((pizza, 0.5))  # Lower confidence for fuzzy
        
        return fuzzy_matches
    
    def _rank_matches(self, direct_matches: List[tuple[Pizza, float]], 
                     ingredient_matches: List[tuple[Pizza, float]],
                     fuzzy_matches: List[tuple[Pizza, float]]) -> List[Pizza]:
        """Combine and rank all matches by confidence score"""
        all_scores = {}
        
        # Combine scores for same pizzas
        for matches in [direct_matches, ingredient_matches, fuzzy_matches]:
            for pizza, score in matches:
                if pizza not in all_scores:
                    all_scores[pizza] = 0
                all_scores[pizza] += score
        
        # Sort by score (highest first)
        sorted_matches = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [pizza for pizza, score in sorted_matches]
    
    def _calculate_confidence(self, query: str, matches: List[Pizza]) -> float:
        """Calculate confidence score for the search results"""
        if not matches:
            return 0.0
        
        # Simple confidence calculation based on number of matches and query clarity
        base_confidence = 0.6
        
        # Boost confidence for direct name matches
        for pizza in matches:
            if pizza.name.replace('_', ' ') in query:
                base_confidence += 0.3
                break
        
        # Reduce confidence for multiple matches (ambiguous query)
        if len(matches) > 3:
            base_confidence -= 0.2
        
        return min(1.0, max(0.0, base_confidence))

class PizzaRecommendationService:
    """Service for pizza recommendations based on user preferences"""
    
    def __init__(self, catalog_service: PizzaCatalogService):
        self.catalog_service = catalog_service
    
    def recommend_similar_pizzas(self, pizza: Pizza, count: int = 3) -> List[Pizza]:
        """Recommend similar pizzas based on ingredients"""
        all_pizzas = self.catalog_service.get_all_pizzas()
        similar_scores = []
        
        for candidate in all_pizzas:
            if candidate.name != pizza.name:
                similarity = self._calculate_similarity(pizza, candidate)
                similar_scores.append((candidate, similarity))
        
        # Sort by similarity and return top recommendations
        similar_scores.sort(key=lambda x: x[1], reverse=True)
        return [pizza for pizza, score in similar_scores[:count]]
    
    def _calculate_similarity(self, pizza1: Pizza, pizza2: Pizza) -> float:
        """Calculate similarity score between two pizzas based on ingredients"""
        ingredients1 = set(pizza1.ingredients)
        ingredients2 = set(pizza2.ingredients)
        
        if not ingredients1 or not ingredients2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(ingredients1.intersection(ingredients2))
        union = len(ingredients1.union(ingredients2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_popular_pizzas(self, count: int = 3) -> List[Pizza]:
        """Get popular pizza recommendations (hardcoded for now)"""
        popular_names = ['pepperoni', 'margherita', 'meat_lovers']
        popular_pizzas = []
        
        for name in popular_names[:count]:
            pizza = self.catalog_service.get_pizza_by_name(name)
            if pizza:
                popular_pizzas.append(pizza)
        
        return popular_pizzas