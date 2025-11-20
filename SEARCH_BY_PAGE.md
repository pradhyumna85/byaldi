# Search by Page Feature

## Overview

The `search_by_page` method allows you to find the most similar pages to an existing page in your index. This is useful for:
- Finding related content within your document collection
- Discovering pages with similar visual layouts or content
- Building recommendation systems based on page similarity
- Clustering similar pages together

## Usage

### Basic Example

```python
from byaldi import RAGMultiModalModel

# Load an existing index
RAG = RAGMultiModalModel.from_index("your_index_name")

# Find the top 5 pages most similar to page 3 of document 0
results = RAG.search_by_page(doc_id=0, page_num=3, k=5)

# Display results
for result in results:
    print(f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score:.4f}")
```

### Parameters

- **doc_id** (int): The document ID of the reference page
- **page_num** (int): The page number of the reference page (1-indexed)
- **k** (int, optional): The number of similar results to return. Default is 10.
- **filter_metadata** (Dict[str, str], optional): Optional metadata filter to apply to results
- **return_base64_results** (bool, optional): Whether to return base64-encoded image results (if stored with index)

### Return Value

Returns a `List[Result]` where each `Result` object contains:
- `doc_id`: The document ID
- `page_num`: The page number (1-indexed)
- `score`: The similarity score (higher is more similar)
- `metadata`: Document metadata (if available)
- `base64`: Base64-encoded image (if `return_base64_results=True` and images were stored)

### Advanced Examples

#### With Metadata Filtering

```python
# Find similar pages, but only from documents with specific metadata
results = RAG.search_by_page(
    doc_id=0,
    page_num=3,
    k=5,
    filter_metadata={"author": "John Doe"}
)
```

#### With Base64 Images

```python
# Get base64-encoded images of similar pages
results = RAG.search_by_page(
    doc_id=0,
    page_num=3,
    k=5,
    return_base64_results=True
)

# Access the base64 image
for result in results:
    if result.base64:
        # You can now use this base64 string to display or process the image
        print(f"Page {result.page_num} has base64 image available")
```

## How It Works

The `search_by_page` method:

1. Retrieves the embedding for the specified page (doc_id, page_num)
2. Computes similarity scores between this embedding and all other page embeddings in the index
3. Returns the top K most similar pages, excluding the query page itself
4. Optionally filters results by metadata

The similarity is computed using the same scoring mechanism as text-based search, ensuring consistent results across different query types.

## Important Notes

- **Page numbering**: Pages are 1-indexed (first page is page 1)
- **Query page exclusion**: The query page itself is automatically excluded from results
- **Error handling**: If the specified page doesn't exist in the index, a `ValueError` is raised
- **Performance**: The method computes similarity against all pages in the index, so performance scales with index size

## Comparison with Text Search

| Feature | `search()` | `search_by_page()` |
|---------|------------|-------------------|
| Input | Text query | Existing page (doc_id, page_num) |
| Use case | Find pages matching a text description | Find pages similar to a known page |
| Embedding | Generated from text | Retrieved from index |
| Self-exclusion | N/A | Query page excluded from results |

## Example Use Cases

### 1. Content Recommendation
```python
# User is viewing page 5 of document 2
# Show them similar pages they might be interested in
similar_pages = RAG.search_by_page(doc_id=2, page_num=5, k=3)
```

### 2. Duplicate Detection
```python
# Find potential duplicates or near-duplicates of a page
similar_pages = RAG.search_by_page(doc_id=0, page_num=1, k=10)
# High similarity scores might indicate duplicates
```

### 3. Visual Layout Clustering
```python
# Find all pages with similar visual layouts to a template page
template_doc_id = 0
template_page_num = 1
similar_layouts = RAG.search_by_page(
    doc_id=template_doc_id,
    page_num=template_page_num,
    k=20
)
```

### 4. Cross-Document Similarity
```python
# Find pages in other documents similar to a page in document 0
results = RAG.search_by_page(doc_id=0, page_num=5, k=10)
# Filter to only show results from different documents
cross_doc_results = [r for r in results if r.doc_id != 0]
```
