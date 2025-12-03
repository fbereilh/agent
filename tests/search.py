from search.data_loader import load_restaurant_data, make_restaurant_doc_with_dishes, make_metadata, load_all_sheets, make_dish_doc, make_dish_metadata
from search import RestaurantVectorStore, DishVectorStore


def test_load_all_sheets():
    """Test that load_all_sheets returns a dictionary of DataFrames with at least one row."""
    result = load_all_sheets()
    
    assert isinstance(result, dict)
    
    for key, df in result.items():
        assert len(df) > 0


def test_document_builder_functions():
    """Test make_restaurant_doc_with_dishes and make_metadata."""
    sheets = load_all_sheets()
    
    # Get available sheet names
    df_restaurants = sheets['restaurants']
    # Check if we have dish data merged already or separate
    dish_sheet_name = 'restaurant_dishes' if 'restaurant_dishes' in sheets else next((k for k in sheets.keys() if 'dish' in k.lower()), None)
    
    if dish_sheet_name:
        df_dishes = sheets[dish_sheet_name]
        
        # Test with first restaurant
        row = df_restaurants.iloc[0]
        
        # Test document builder (may need empty df if no dishes match)
        doc = make_restaurant_doc_with_dishes(row, df_dishes)
        assert isinstance(doc, str)
        assert len(doc) > 20
        assert row['name'] in doc
        
        # Test metadata builder
        metadata = make_metadata(row)
        assert isinstance(metadata, dict)
        assert 'restaurant_id' in metadata
        assert 'name' in metadata
        assert metadata['name'] == row['name']


def test_restaurant_vector_store_indexing():
    """Test indexing restaurants into vector store."""
    df_restaurants, df_dishes = load_restaurant_data()
    
    store = RestaurantVectorStore(db_path="test_chromadb")
    store.index_restaurants(df_restaurants, df_dishes, force_reindex=True)
    
    count = store.count()
    assert count > 15
    assert count == len(df_restaurants)


def test_dish_vector_store_indexing():
    """Test indexing dishes into vector store."""
    df_restaurants, df_dishes = load_restaurant_data()
    
    store = DishVectorStore(db_path="test_chromadb")
    store.index_dishes(df_dishes, df_restaurants, force_reindex=True)
    
    count = store.count()
    assert count > 600  # We have 697 dishes
    assert count == len(df_dishes)
    
    # Test search functionality
    results = store.search("pasta", n_results=3)
    assert 'ids' in results
    assert len(results['ids'][0]) > 1
    
    # Test dish doc builder
    row = df_dishes.iloc[0]
    doc = make_dish_doc(row)
    assert isinstance(doc, str)
    assert len(doc) > 10
    
    # Test dish metadata builder
    metadata = make_dish_metadata(row, df_restaurants)
    assert isinstance(metadata, dict)
    assert 'dish_id' in metadata
    assert 'restaurant_id' in metadata
    assert 'restaurant_name' in metadata
