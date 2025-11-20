# Quick Start: Search by Page

## What is it?

`search_by_page()` finds the most similar pages to an existing page in your Byaldi index. Instead of using a text query, you specify a page by its `doc_id` and `page_num`.

## Quick Example

```python
from byaldi import RAGMultiModalModel

# Load your index
RAG = RAGMultiModalModel.from_index("my_index")

# Find top 5 pages similar to page 3 of document 0
results = RAG.search_by_page(doc_id=0, page_num=3, k=5)

# Print results
for r in results:
    print(f"Doc {r.doc_id}, Page {r.page_num}: {r.score:.2f}")
```

## When to use it?

- **Content recommendation**: "Show me pages similar to this one"
- **Duplicate detection**: "Find near-duplicate pages"
- **Visual clustering**: "Find pages with similar layouts"
- **Related content**: "Find related pages across documents"

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `doc_id` | int | Yes | - | Document ID of the reference page |
| `page_num` | int | Yes | - | Page number (1-indexed) |
| `k` | int | No | 10 | Number of results to return |
| `filter_metadata` | dict | No | None | Filter results by metadata |
| `return_base64_results` | bool | No | None | Return base64 images |

## Result Format

Each result is a `Result` object with:
- `doc_id`: Document ID
- `page_num`: Page number (1-indexed)
- `score`: Similarity score (higher = more similar)
- `metadata`: Document metadata (if available)
- `base64`: Base64 image (if requested and available)

## Important Notes

1. **Page numbering**: Pages start at 1 (not 0)
2. **Self-exclusion**: The query page is automatically excluded from results
3. **Error handling**: Raises `ValueError` if the page doesn't exist in the index

## Comparison with Text Search

```python
# Text search: Find pages matching a query
results = RAG.search("machine learning", k=5)

# Page search: Find pages similar to a specific page
results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
```

## Common Patterns

### Find similar pages in the same document
```python
results = RAG.search_by_page(doc_id=5, page_num=10, k=5)
same_doc = [r for r in results if r.doc_id == 5]
```

### Find similar pages in other documents
```python
results = RAG.search_by_page(doc_id=5, page_num=10, k=5)
other_docs = [r for r in results if r.doc_id != 5]
```

### Filter by metadata
```python
results = RAG.search_by_page(
    doc_id=0,
    page_num=3,
    k=5,
    filter_metadata={"category": "technical"}
)
```

### Get images with results
```python
results = RAG.search_by_page(
    doc_id=0,
    page_num=3,
    k=5,
    return_base64_results=True
)
```

## Next Steps

- See `SEARCH_BY_PAGE.md` for detailed documentation
- See `example_search_by_page.py` for a complete working example
- Run `pytest tests/test_e2e_rag.py::test_search_by_page` to see it in action
