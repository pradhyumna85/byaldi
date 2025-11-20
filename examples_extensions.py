"""
Examples showing different ways to use byaldi_extensions.py
without modifying the Byaldi package code.
"""

# =============================================================================
# OPTION 1: Standalone Function (No modification to Byaldi)
# =============================================================================
def example_standalone_function():
    """Use search_by_page as a standalone function."""
    print("\n" + "="*80)
    print("OPTION 1: Standalone Function")
    print("="*80)
    
    from byaldi import RAGMultiModalModel
    from byaldi_extensions import search_by_page
    
    # Load index normally
    RAG = RAGMultiModalModel.from_index("your_index_name")
    
    # Use the standalone function
    results = search_by_page(RAG, doc_id=0, page_num=3, k=5)
    
    # Display results
    print(f"\nTop 5 pages similar to doc_id=0, page_num=3:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Doc {result.doc_id}, Page {result.page_num}: {result.score:.4f}")


# =============================================================================
# OPTION 2: Monkey Patch (Adds method to existing classes)
# =============================================================================
def example_monkey_patch():
    """Patch Byaldi classes to add the method."""
    print("\n" + "="*80)
    print("OPTION 2: Monkey Patch")
    print("="*80)
    
    # Patch BEFORE importing/using Byaldi
    from byaldi_extensions import patch_search_by_page
    patch_search_by_page()
    
    # Now use Byaldi normally - the method is available!
    from byaldi import RAGMultiModalModel
    RAG = RAGMultiModalModel.from_index("your_index_name")
    
    # The method is now part of the class
    results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
    
    # Display results
    print(f"\nTop 5 pages similar to doc_id=0, page_num=3:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Doc {result.doc_id}, Page {result.page_num}: {result.score:.4f}")


# =============================================================================
# OPTION 3: Wrapper Class (No modification, clean interface)
# =============================================================================
def example_wrapper_class():
    """Use the wrapper class that extends functionality."""
    print("\n" + "="*80)
    print("OPTION 3: Wrapper Class")
    print("="*80)
    
    from byaldi_extensions import ExtendedRAGMultiModalModel
    
    # Use the extended class instead of RAGMultiModalModel
    RAG = ExtendedRAGMultiModalModel.from_index("your_index_name")
    
    # All original methods work
    text_results = RAG.search("some query", k=3)
    print(f"\nText search returned {len(text_results)} results")
    
    # Plus the new method
    page_results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
    
    # Display results
    print(f"\nTop 5 pages similar to doc_id=0, page_num=3:")
    for i, result in enumerate(page_results, 1):
        print(f"{i}. Doc {result.doc_id}, Page {result.page_num}: {result.score:.4f}")


# =============================================================================
# OPTION 4: Auto-patch via Environment Variable
# =============================================================================
def example_auto_patch():
    """Automatically patch on import using environment variable."""
    print("\n" + "="*80)
    print("OPTION 4: Auto-patch via Environment Variable")
    print("="*80)
    
    import os
    
    # Set environment variable BEFORE importing
    os.environ["BYALDI_AUTO_PATCH"] = "1"
    
    # Now when you import byaldi_extensions, it auto-patches
    import byaldi_extensions  # This triggers the auto-patch
    
    # Use Byaldi normally
    from byaldi import RAGMultiModalModel
    RAG = RAGMultiModalModel.from_index("your_index_name")
    
    # Method is available
    results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
    
    print("\nAuto-patched! Method is available on RAGMultiModalModel")


# =============================================================================
# COMPARISON: Which option to choose?
# =============================================================================
def print_comparison():
    """Print comparison of different approaches."""
    print("\n" + "="*80)
    print("COMPARISON: Which Option Should You Choose?")
    print("="*80)
    
    comparison = """
    ┌─────────────────────┬──────────────┬──────────────┬─────────────────┐
    │ Feature             │ Standalone   │ Monkey Patch │ Wrapper Class   │
    ├─────────────────────┼──────────────┼──────────────┼─────────────────┤
    │ Modifies Byaldi     │ No           │ Yes (runtime)│ No              │
    │ Clean API           │ Moderate     │ Excellent    │ Excellent       │
    │ Easy to use         │ Good         │ Excellent    │ Excellent       │
    │ Type hints work     │ Partial      │ Yes          │ Yes             │
    │ IDE autocomplete    │ No           │ Yes          │ Yes             │
    │ Risk of conflicts   │ None         │ Low          │ None            │
    │ Performance         │ Same         │ Same         │ Tiny overhead   │
    └─────────────────────┴──────────────┴──────────────┴─────────────────┘
    
    RECOMMENDATIONS:
    
    1. Use STANDALONE FUNCTION if:
       - You want zero risk of conflicts
       - You only need it occasionally
       - You're in a very restricted environment
    
    2. Use MONKEY PATCH if:
       - You want the cleanest API
       - You use the method frequently
       - You want IDE autocomplete
       - You're okay with runtime modifications
    
    3. Use WRAPPER CLASS if:
       - You want clean API without modifications
       - You're building a library on top of Byaldi
       - You want to add multiple custom methods
       - You need maximum safety
    
    4. Use AUTO-PATCH if:
       - You want convenience
       - You control the environment
       - You want to set it once and forget
    """
    print(comparison)


# =============================================================================
# REAL WORLD EXAMPLE: Using in a production environment
# =============================================================================
def production_example():
    """Example of using in production where you can't modify packages."""
    print("\n" + "="*80)
    print("PRODUCTION EXAMPLE")
    print("="*80)
    
    # In production, you typically want the wrapper class approach
    # because it's safe and doesn't modify the original package
    
    from byaldi_extensions import ExtendedRAGMultiModalModel
    
    class DocumentSimilarityService:
        """A service that finds similar documents."""
        
        def __init__(self, index_name: str):
            # Use the extended model
            self.rag = ExtendedRAGMultiModalModel.from_index(index_name)
        
        def find_similar_pages(self, doc_id: int, page_num: int, limit: int = 5):
            """Find similar pages to a given page."""
            return self.rag.search_by_page(
                doc_id=doc_id,
                page_num=page_num,
                k=limit
            )
        
        def search_text(self, query: str, limit: int = 5):
            """Search by text query."""
            return self.rag.search(query, k=limit)
    
    # Use the service
    service = DocumentSimilarityService("your_index_name")
    
    # Find similar pages
    similar = service.find_similar_pages(doc_id=0, page_num=3, limit=5)
    print(f"\nFound {len(similar)} similar pages")
    
    # Also works with text search
    text_results = service.search_text("machine learning", limit=3)
    print(f"Found {len(text_results)} text search results")


# =============================================================================
# Main: Run examples
# =============================================================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("BYALDI EXTENSIONS - USAGE EXAMPLES")
    print("="*80)
    print("\nThese examples show how to use search_by_page without modifying")
    print("the Byaldi package code.")
    
    # Print comparison first
    print_comparison()
    
    print("\n" + "="*80)
    print("To run the actual examples, uncomment the function calls below")
    print("and update 'your_index_name' to your actual index name.")
    print("="*80)
    
    # Uncomment to run examples (requires an actual index):
    # example_standalone_function()
    # example_monkey_patch()
    # example_wrapper_class()
    # example_auto_patch()
    # production_example()
