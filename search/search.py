"""Restaurant search functionality with vector store."""

import chromadb
from chromadb.api.models.Collection import Collection
import pandas as pd
from typing import List, Dict, Any, Optional

from .data_loader import load_restaurant_data, make_restaurant_doc_with_dishes, make_metadata, make_dish_doc, make_dish_metadata


class RestaurantVectorStore:
    """Manages ChromaDB vector store for restaurant search."""
    
    def __init__(self, db_path: str = "chromadb", collection_name: str = "restaurants"):
        """
        Initialize the vector store.
        
        Args:
            db_path: Path to ChromaDB persistent storage
            collection_name: Name of the collection to use
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection: Optional[Collection] = None
        
    def create_or_get_collection(self) -> Collection:
        """Get or create the collection."""
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        return self.collection
    
    def delete_collection(self) -> None:
        """Delete the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def index_restaurants(
        self, 
        df_restaurants: pd.DataFrame, 
        df_dishes: pd.DataFrame,
        top_n_dishes: int = 10,
        force_reindex: bool = False
    ) -> None:
        """
        Index all restaurants into the vector store.
        
        Args:
            df_restaurants: DataFrame with restaurant data
            df_dishes: DataFrame with dish data
            top_n_dishes: Number of top dishes to include per restaurant
            force_reindex: If True, delete and recreate the collection
        """
        if force_reindex:
            self.delete_collection()
        
        if self.collection is None:
            self.create_or_get_collection()
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df_restaurants.iterrows():
            documents.append(make_restaurant_doc_with_dishes(row, df_dishes, top_n_dishes))
            metadatas.append(make_metadata(row))
            ids.append(f"rest_{row['id']}")
        
        # Use upsert to add or update documents
        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"Indexed {len(documents)} restaurants")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for restaurants matching the query.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            where: Filter on metadata (e.g., {"price_level": "low"})
            where_document: Filter on document content
            
        Returns:
            Dictionary with search results
        """
        if self.collection is None:
            self.create_or_get_collection()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return results
    
    def get_by_id(self, restaurant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific restaurant by ID.
        
        Args:
            restaurant_id: Restaurant ID
            
        Returns:
            Dictionary with restaurant data or None if not found
        """
        if self.collection is None:
            self.create_or_get_collection()
        
        try:
            result = self.collection.get(ids=[f"rest_{restaurant_id}"])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
        except Exception as e:
            print(f"Error getting restaurant {restaurant_id}: {e}")
        
        return None
    
    def count(self) -> int:
        """Get the number of documents in the collection."""
        if self.collection is None:
            self.create_or_get_collection()
        return self.collection.count()


class DishVectorStore:
    """Manages ChromaDB vector store for dish search."""
    
    def __init__(self, db_path: str = "chromadb", collection_name: str = "dishes"):
        """
        Initialize the dish vector store.
        
        Args:
            db_path: Path to ChromaDB persistent storage
            collection_name: Name of the collection to use
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection: Optional[Collection] = None
        
    def create_or_get_collection(self) -> Collection:
        """Get or create the collection."""
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        return self.collection
    
    def delete_collection(self) -> None:
        """Delete the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def index_dishes(
        self, 
        df_dishes: pd.DataFrame,
        df_restaurants: pd.DataFrame,
        force_reindex: bool = False
    ) -> None:
        """
        Index all dishes into the vector store.
        
        Args:
            df_dishes: DataFrame with dish data
            df_restaurants: DataFrame with restaurant data for enrichment
            force_reindex: If True, delete and recreate the collection
        """
        if force_reindex:
            self.delete_collection()
        
        if self.collection is None:
            self.create_or_get_collection()
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in df_dishes.iterrows():
            documents.append(make_dish_doc(row))
            metadatas.append(make_dish_metadata(row, df_restaurants))
            ids.append(f"dish_{row['restaurant_id']}_{row['dish_id']}")
        
        # Use upsert to add or update documents
        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"Indexed {len(documents)} dishes")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for dishes matching the query.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            where: Filter on metadata
            where_document: Filter on document content
            
        Returns:
            Dictionary with search results
        """
        if self.collection is None:
            self.create_or_get_collection()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return results
    
    def count(self) -> int:
        """Get the number of documents in the collection."""
        if self.collection is None:
            self.create_or_get_collection()
        return self.collection.count()


class RestaurantSearch:
    """High-level interface for restaurant search."""
    
    _instance = None  # Singleton instance for agent tools
    
    def __init__(self, db_path: str = "chromadb", auto_load: bool = False):
        """
        Initialize the restaurant search interface.
        
        Args:
            db_path: Path to ChromaDB storage
            auto_load: If True, automatically load and index data
        """
        self.vector_store = RestaurantVectorStore(db_path=db_path)
        self.dish_vector_store = DishVectorStore(db_path=db_path)
        self.df_restaurants: Optional[pd.DataFrame] = None
        self.df_dishes: Optional[pd.DataFrame] = None
        
        # Set as singleton instance for agent tools
        RestaurantSearch._instance = self
        
        if auto_load:
            self.load_and_index()
    
    def load_and_index(
        self, 
        sheet_id: Optional[str] = None,
        force_reindex: bool = False,
        top_n_dishes: int = 10
    ) -> None:
        """
        Load data and index restaurants and dishes.
        
        Args:
            sheet_id: Optional Google Sheets ID (uses default if not provided)
            force_reindex: If True, delete and recreate the index
            top_n_dishes: Number of top dishes to include per restaurant
        """
        # Check if data already indexed (skip if not force_reindex)
        if not force_reindex:
            # Initialize collections to check counts
            restaurant_collection = self.vector_store.create_or_get_collection()
            dish_collection = self.dish_vector_store.create_or_get_collection()
            
            restaurant_count = restaurant_collection.count()
            dish_count = dish_collection.count()
            
            if restaurant_count > 0 and dish_count > 0:
                print(f"Data already indexed: {restaurant_count} restaurants, {dish_count} dishes")
                print("Skipping indexing. Use force_reindex=True to re-index.")
                return
        
        print("Loading restaurant data...")
        if sheet_id:
            self.df_restaurants, self.df_dishes = load_restaurant_data(sheet_id)
        else:
            self.df_restaurants, self.df_dishes = load_restaurant_data()
        
        print(f"Loaded {len(self.df_restaurants)} restaurants and {len(self.df_dishes)} dishes")
        
        print("Indexing restaurants...")
        self.vector_store.index_restaurants(
            self.df_restaurants, 
            self.df_dishes,
            top_n_dishes=top_n_dishes,
            force_reindex=force_reindex
        )
        print("Indexing complete!")
        
        # Index dishes separately
        if len(self.df_dishes) > 0:
            print("Indexing dishes...")
            self.dish_vector_store.index_dishes(
                self.df_dishes,
                self.df_restaurants,
                force_reindex=force_reindex
            )
            print("Dish indexing complete!")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        price_level: Optional[str] = None,
        zone: Optional[str] = None,
        has_vegetarian: Optional[bool] = None,
        has_vegan: Optional[bool] = None,
        has_gluten_free: Optional[bool] = None,
        has_takeaway: Optional[bool] = None,
        has_bar: Optional[bool] = None,
        has_menu: Optional[bool] = None,
        allow_reservations: Optional[bool] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        opening_time: Optional[str] = None,
        closing_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for restaurants with optional filters.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            price_level: Filter by price level ("low", "medium", "high")
            zone: Filter by mall zone
            has_vegetarian: Filter for vegetarian options
            has_vegan: Filter for vegan options
            has_gluten_free: Filter for gluten-free options
            has_takeaway: Filter for takeaway service
            has_bar: Filter for bar service
            has_menu: Filter for restaurants with set menu
            allow_reservations: Filter for restaurants that accept reservations
            latitude: Filter by latitude coordinate
            longitude: Filter by longitude coordinate
            opening_time: Filter by opening time (e.g., "10:00")
            closing_time: Filter by closing time (e.g., "22:00")
            
        Returns:
            List of restaurant results with metadata
        """
        # Build where clause from filters
        where = {}
        if price_level:
            where["price_level"] = price_level
        if zone:
            where["zone"] = zone
        if has_vegetarian is not None:
            where["has_vegetarian"] = has_vegetarian
        if has_vegan is not None:
            where["has_vegan"] = has_vegan
        if has_gluten_free is not None:
            where["has_gluten_free"] = has_gluten_free
        if has_takeaway is not None:
            where["has_takeaway"] = has_takeaway
        if has_bar is not None:
            where["has_bar"] = has_bar
        if has_menu is not None:
            where["has_menu"] = has_menu
        if allow_reservations is not None:
            where["allow_reservations"] = allow_reservations
        if latitude is not None:
            where["latitude"] = latitude
        if longitude is not None:
            where["longitude"] = longitude
        if opening_time is not None:
            where["opening_time"] = opening_time
        if closing_time is not None:
            where["closing_time"] = closing_time
        
        # Perform search
        results = self.vector_store.search(
            query=query,
            n_results=n_results,
            where=where if where else None
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_restaurant(self, restaurant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific restaurant by ID.
        
        Args:
            restaurant_id: Restaurant ID
            
        Returns:
            Restaurant data or None if not found
        """
        return self.vector_store.get_by_id(restaurant_id)
    
    def get_restaurant_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific restaurant by name.
        
        Args:
            name: Restaurant name
            
        Returns:
            Restaurant data or None if not found
        """
        if self.vector_store.collection is None:
            self.vector_store.create_or_get_collection()
        
        try:
            result = self.vector_store.collection.get(where={"name": name})
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
        except Exception as e:
            print(f"Error getting restaurant {name}: {e}")
        
        return None
    
    def count(self) -> int:
        """Get the number of indexed restaurants."""
        return self.vector_store.count()
    
    def search_dishes(
        self,
        query: str,
        n_results: int = 5,
        restaurant_name: Optional[str] = None,
        zone: Optional[str] = None,
        price_level: Optional[str] = None,
        has_vegetarian: Optional[bool] = None,
        has_vegan: Optional[bool] = None,
        has_gluten_free: Optional[bool] = None,
        has_halal: Optional[bool] = None,
        has_lactose_free: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for dishes with optional filters.
        
        Args:
            query: Search query text for dish names/descriptions
            n_results: Number of results to return
            restaurant_name: Filter by specific restaurant name
            zone: Filter by restaurant zone
            price_level: Filter by restaurant price level
            has_vegetarian: Filter for vegetarian dishes
            has_vegan: Filter for vegan dishes
            has_gluten_free: Filter for gluten-free dishes
            has_halal: Filter for halal dishes
            has_lactose_free: Filter for lactose-free dishes
            category: Filter by dish category
            
        Returns:
            List of dish results with metadata including restaurant info
        """
        # Build where clause from filters
        where = {}
        if restaurant_name:
            where["restaurant_name"] = restaurant_name
        if zone:
            where["zone"] = zone
        if price_level:
            where["price_level"] = price_level
        if has_vegetarian is not None:
            where["has_vegetarian"] = has_vegetarian
        if has_vegan is not None:
            where["has_vegan"] = has_vegan
        if has_gluten_free is not None:
            where["has_gluten_free"] = has_gluten_free
        if has_halal is not None:
            where["has_halal"] = has_halal
        if has_lactose_free is not None:
            where["has_lactose_free"] = has_lactose_free
        if category:
            where["category"] = category
        
        # Perform search
        results = self.dish_vector_store.search(
            query=query,
            n_results=n_results,
            where=where if where else None
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def count_dishes(self) -> int:
        """Get the number of indexed dishes."""
        return self.dish_vector_store.count()
    
    def get_available_zones(self) -> List[str]:
        """Get list of available zones."""
        if self.df_restaurants is None:
            return []
        zones = self.df_restaurants['zone'].dropna().unique().tolist()
        return sorted(zones)
    
    def get_available_price_levels(self) -> List[str]:
        """Get list of available price levels."""
        if self.df_restaurants is None:
            return []
        return sorted(self.df_restaurants['price_level'].dropna().unique().tolist())
