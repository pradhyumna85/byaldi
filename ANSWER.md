# How to Find Top K Similar Pages in Byaldi

## Answer

I've implemented a new `search_by_page()` method that allows you to find the most similar pages to an existing page in your Byaldi index using `doc_id` and `page_num`.

## Usage

```python
from byaldi import RAGMultiModalModel

# Load your index
RAG = RAGMultiModalModel.from_index("your_index_name")

# Find top K similar pages to a specific page
results = RAG.search_by_page(
    doc_id=0,        # Document ID
    page_num=3,      # Page number (1-indexed)
    k=5              # Number of results
)

# Display results
for result in results:
    print(f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score:.4f}")
```

## What Was Implemented

### 1. Core Method (`byaldi/colpali.py`)
Added `search_by_page()` method to the `ColPaliModel` class that:
- Retrieves the embedding for the specified page
- Computes similarity scores against all other page embeddings
- Returns top K most similar pages (excluding the query page itself)
- Supports metadata filtering and base64 image results

### 2. Public API (`byaldi/RAGModel.py`)
Exposed the method through `RAGMultiModalModel` class for easy access.

### 3. Tests (`tests/test_e2e_rag.py`)
Added comprehensive test case `test_search_by_page()` to verify functionality.

### 4. Documentation
Created three documentation files:
- `SEARCH_BY_PAGE.md` - Detailed documentation with examples
- `QUICK_START_SEARCH_BY_PAGE.md` - Quick reference guide
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details

### 5. Example Script
Created `example_search_by_page.py` - Working example you can run.

## Key Features

✅ **Simple API**: Just provide `doc_id`, `page_num`, and `k`  
✅ **Metadata filtering**: Filter results by document metadata  
✅ **Base64 images**: Optionally return images with results  
✅ **Self-exclusion**: Query page automatically excluded from results  
✅ **Error handling**: Clear error if page doesn't exist  
✅ **Consistent**: Uses same scoring mechanism as text search  

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `doc_id` | int | ✓ | - | Document ID of reference page |
| `page_num` | int | ✓ | - | Page number (1-indexed) |
| `k` | int | ✗ | 10 | Number of results to return |
| `filter_metadata` | dict | ✗ | None | Filter by metadata |
| `return_base64_results` | bool | ✗ | None | Return base64 images |

## Advanced Examples

### Filter by metadata
```python
results = RAG.search_by_page(
    doc_id=0,
    page_num=3,
    k=5,
    filter_metadata={"author": "John Doe"}
)
```

### Get base64 images
```python
results = RAG.search_by_page(
    doc_id=0,
    page_num=3,
    k=5,
    return_base64_results=True
)
```

### Find cross-document similarities
```python
results = RAG.search_by_page(doc_id=0, page_num=5, k=10)
other_docs = [r for r in results if r.doc_id != 0]
```

## How It Works

1. **Lookup**: Finds the embedding for the specified page in the index
2. **Score**: Computes similarity between this embedding and all others using `processor.score()`
3. **Rank**: Sorts by similarity score (highest first)
4. **Filter**: Excludes the query page and applies any metadata filters
5. **Return**: Returns top K results as `Result` objects

## Files Modified/Created

**Modified:**
- `byaldi/colpali.py` - Added `search_by_page()` method
- `byaldi/RAGModel.py` - Exposed method in public API
- `tests/test_e2e_rag.py` - Added test case

**Created:**
- `SEARCH_BY_PAGE.md` - Comprehensive documentation
- `QUICK_START_SEARCH_BY_PAGE.md` - Quick reference
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `example_search_by_page.py` - Working example
- `ANSWER.md` - This file

## Testing

Run the test with:
```bash
pytest tests/test_e2e_rag.py::test_search_by_page -v
```

## Next Steps

1. Load your existing index
2. Try the example: `python example_search_by_page.py` (update index name first)
3. Integrate into your application
4. See `SEARCH_BY_PAGE.md` for more advanced use cases

The implementation is complete, tested, and ready to use!
