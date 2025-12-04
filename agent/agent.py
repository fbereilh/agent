"""Restaurant recommendation chat agent with search and location tools."""

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from dotenv import load_dotenv
from lisette.core import Chat, Message

from search import RestaurantSearch


load_dotenv()



def get_system_prompt():
    """Generate system prompt with current context."""
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%A, %d de %B de %Y")
    
    # Determine if it's meal time
    hour = now.hour
    if 7 <= hour < 11:
        meal_context = "- Es hora de desayuno."
    elif 13 <= hour < 16:
        meal_context = "- Es hora de almuerzo."
    elif 19 <= hour < 22:
        meal_context = "- Es hora de cena."
    else:
        meal_context = ""
    
    # Load prompt template from file
    prompt_file = Path(__file__).parent / "system_prompt.txt"
    template = prompt_file.read_text(encoding="utf-8")
    
    # Format with current context
    return template.format(
        current_date=current_date,
        current_time=current_time,
        meal_context=meal_context
    )


def search_restaurants(
    query: str,  # Natural language search query (e.g., "Italian food", "gluten free", "cheap lunch", "north zone")
    n_results: int = 3,  # Number of results to return
    price_level: str = None,  # Filter by price: "low", "medium", or "high"
    zone: str = None,  # Filter by mall zone: "north", "center", or "south"
    has_vegetarian: bool = None,  # Filter for vegetarian options
    has_vegan: bool = None,  # Filter for vegan options
    has_gluten_free: bool = None,  # Filter for gluten-free options
    has_takeaway: bool = None,  # Filter for takeaway service
    has_bar: bool = None,  # Filter for restaurants with bar service
    has_menu: bool = None,  # Filter for restaurants with available menu
    allow_reservations: bool = None,  # Filter for restaurants that accept reservations
    open_now: bool = None,  # Filter for restaurants currently open
    open_at_time: str = None  # Filter for restaurants open at specific time (format: "HH:MM", e.g., "14:30")
) -> str:
    """Search for restaurants in the mall based on user preferences.
    
    Returns formatted restaurant information including descriptions, cuisine types, dietary options, 
    menu highlights, location zone, services, hours, and contact details."""
    
    # Initialize search
    search = RestaurantSearch._instance
    if search is None:
        search = RestaurantSearch(db_path="chromadb")
        search.load_and_index()
    
    # Build filter kwargs
    filter_kwargs = {}
    if price_level:
        filter_kwargs['price_level'] = price_level
    if zone:
        filter_kwargs['zone'] = zone
    if has_vegetarian is not None:
        filter_kwargs['has_vegetarian'] = has_vegetarian
    if has_vegan is not None:
        filter_kwargs['has_vegan'] = has_vegan
    if has_gluten_free is not None:
        filter_kwargs['has_gluten_free'] = has_gluten_free
    if has_takeaway is not None:
        filter_kwargs['has_takeaway'] = has_takeaway
    if has_bar is not None:
        filter_kwargs['has_bar'] = has_bar
    if has_menu is not None:
        filter_kwargs['has_menu'] = has_menu
    if allow_reservations is not None:
        filter_kwargs['allow_reservations'] = allow_reservations
    
    # Get results
    results = search.search(query=query, n_results=n_results, **filter_kwargs)
    
    # Post-filter by time if needed
    if open_now or open_at_time:
        madrid_tz = ZoneInfo("Europe/Madrid")
        check_time = open_at_time if open_at_time else datetime.now(madrid_tz).strftime("%H:%M")
        
        filtered_results = []
        for result in results:
            meta = result['metadata']
            opening = meta.get('opening_time', '')
            closing = meta.get('closing_time', '')
            
            if opening and closing and opening <= check_time <= closing:
                filtered_results.append(result)
        
        results = filtered_results
    
    # Format results for the LLM
    formatted = "<valid>\n"
    for result in results:
        meta = result['metadata']
        doc = result['document']
        
        formatted += f"\n## {meta['name']}\n"
        formatted += f"{doc}\n"
        # Only add contact info if available
        if meta.get('phone'):
            formatted += f"Phone: {meta['phone']}\n"
        
        if meta.get('website_url'):
            formatted += f"Website: {meta['website_url']}\n"    
            
    # Close valid tag
    formatted += "</valid>"
    
    return formatted


def get_walking_time(
    from_restaurant: str,  # Name of starting restaurant
    to_restaurant: str,  # Name of destination restaurant
) -> str:
    """Calculate walking time in minutes between two restaurants in the mall.
    
    Returns the estimated walking time rounded to 1 decimal place.
    Walking speed is calibrated to mall conditions (approximately 69 meters per minute)."""
    
    # Initialize search
    search = RestaurantSearch._instance
    if search is None:
        search = RestaurantSearch(db_path="chromadb")
        search.load_and_index()
    
    # Get both restaurants
    from_rest = search.get_restaurant_by_name(from_restaurant)
    to_rest = search.get_restaurant_by_name(to_restaurant)
    
    # Check if restaurants exist
    if not from_rest or not to_rest:
        return "Restaurant not found"
    
    # Extract coordinates from metadata
    from_meta = from_rest['metadata']
    to_meta = to_rest['metadata']
    
    from_lat = from_meta['latitude']
    from_lon = from_meta['longitude']
    to_lat = to_meta['latitude']
    to_lon = to_meta['longitude']
    
    # Calculate distance using numpy
    avg_lat = np.radians((from_lat + to_lat) / 2)
    lat_m = (to_lat - from_lat) * 111320
    lon_m = (to_lon - from_lon) * 111320 * np.cos(avg_lat)
    distance_m = np.sqrt(lat_m**2 + lon_m**2)
    
    # Calculate time
    time_mins = distance_m / 69
    
    return f"<valid>\nWalking time from {from_restaurant} to {to_restaurant}: {np.round(time_mins, 1)} minutes\n</valid>"


def search_dishes(
    query: str,  # Natural language search query for specific dishes (e.g., "carbonara", "vegan burger", "tiramisu")
    n_results: int = 5,  # Number of dish results to return
    restaurant_name: str = None,  # Filter by specific restaurant name
    zone: str = None,  # Filter by mall zone: "north", "center", or "south"
    price_level: str = None,  # Filter by restaurant price: "low", "medium", or "high"
    has_vegetarian: bool = None,  # Filter for vegetarian dishes only
    has_vegan: bool = None,  # Filter for vegan dishes only
    has_gluten_free: bool = None,  # Filter for gluten-free dishes only
    has_halal: bool = None,  # Filter for halal dishes only
    has_lactose_free: bool = None,  # Filter for lactose-free dishes only
    category: str = None,  # Filter by dish category
) -> str:
    """Search for specific dishes across all restaurants in the mall.
    
    Use this when users ask about specific dishes (like "pasta", "burger", "dessert") rather than general restaurant recommendations.
    Returns dish information with the restaurant name and location where each dish is available."""
    
    # Initialize search
    search = RestaurantSearch._instance
    if search is None:
        search = RestaurantSearch(db_path="chromadb")
        search.load_and_index()
    
    # Build filter kwargs
    filter_kwargs = {}
    if restaurant_name:
        filter_kwargs['restaurant_name'] = restaurant_name
    if zone:
        filter_kwargs['zone'] = zone
    if price_level:
        filter_kwargs['price_level'] = price_level
    if has_vegetarian is not None:
        filter_kwargs['has_vegetarian'] = has_vegetarian
    if has_vegan is not None:
        filter_kwargs['has_vegan'] = has_vegan
    if has_gluten_free is not None:
        filter_kwargs['has_gluten_free'] = has_gluten_free
    if has_halal is not None:
        filter_kwargs['has_halal'] = has_halal
    if has_lactose_free is not None:
        filter_kwargs['has_lactose_free'] = has_lactose_free
    if category:
        filter_kwargs['category'] = category
    
    # Get results
    results = search.search_dishes(query=query, n_results=n_results, **filter_kwargs)
    
    # Format results for the LLM
    formatted = "<valid>\n"
    
    # Group dishes by restaurant for better presentation
    dishes_by_restaurant = {}
    for result in results:
        meta = result['metadata']
        rest_name = meta.get('restaurant_name', 'Unknown')
        if rest_name not in dishes_by_restaurant:
            dishes_by_restaurant[rest_name] = []
        dishes_by_restaurant[rest_name].append(result)
    
    for rest_name, dishes in dishes_by_restaurant.items():
        formatted += f"\n## At {rest_name}"
        if dishes and dishes[0]['metadata'].get('zone'):
            formatted += f" ({dishes[0]['metadata']['zone']} zone)"
        formatted += "\n"
        
        for result in dishes:
            doc = result['document']
            formatted += f"- {doc}\n"
    
    # Close valid tag
    formatted += "</valid>"
    
    return formatted


class RestaurantAgent:
    """Chat agent for restaurant recommendations."""
    
    def __init__(self, model=None, temp=0.5, db_path="chromadb"):
        """Initialize the agent.
        
        Args:
            model: LLM model to use (defaults to AGENT_MODEL env var or "claude-haiku-4-5-20251001")
            temp: Temperature for LLM
            db_path: Path to ChromaDB database
        """
        if model is None:
            model = os.getenv("AGENT_MODEL", "claude-haiku-4-5-20251001")
        
        # Initialize search
        self.search = RestaurantSearch(db_path=db_path)
        self.search.load_and_index()
        
        # Initialize chat
        self.chat = Chat(
            model=model,
            sp=get_system_prompt(),
            temp=temp,
            tools=[search_restaurants, search_dishes, get_walking_time]
        )
        
        # Add welcome message
        first_message = Message(
            role='assistant',
            content="""¡Hola! 👋 Soy tu asistente virtual de La Roca Village. 
Estoy aquí para ayudarte a encontrar el restaurante perfecto según tus preferencias. Puedo ayudarte con:\n\n

• Recomendaciones de restaurantes según tipo de cocina\n
• Opciones dietéticas (vegetariano, vegano, sin gluten)\n
• Ubicación de restaurantes en el centro comercial\n
• Información sobre precios y horarios\n\n
"""
        )
        self.chat.hist.append(first_message)
    
    def __call__(self, message: str):
        """Send a message to the agent and get response.
        
        Args:
            message: User message
        
        Returns:
            Agent response
        """
        return self.chat(message)
    
    @property
    def history(self):
        """Get chat history."""
        return self.chat.hist
