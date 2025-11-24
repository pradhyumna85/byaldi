# Search by Image - Usage Guide

The `byaldi_extensions.py` module now includes `search_by_image` functionality that allows you to find similar images in your Byaldi index using a PIL Image as the query.

## Features

- **PIL Image Input**: Takes a PIL Image directly as the query
- **Embedding Generation**: Uses the model's processor to convert the image to embeddings
- **Similarity Search**: Scores the image embedding against all indexed embeddings
- **Metadata Filtering**: Supports optional metadata filtering
- **Flexible Results**: Returns top-k results with optional base64 image data

## Usage Options

### Option 1: Standalone Function

```python
from byaldi import RAGMultiModalModel
from byaldi_extensions import search_by_image
from PIL import Image

# Load your index
RAG = RAGMultiModalModel.from_index("my_index")

# Load a query image
query_image = Image.open("query.png")

# Search for similar images
results = search_by_image(RAG, query_image, k=5)

# Process results
for result in results:
    print(f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score}")
```

### Option 2: Monkey Patching

```python
from byaldi_extensions import patch_search_by_image
from byaldi import RAGMultiModalModel
from PIL import Image

# Patch the Byaldi classes
patch_search_by_image()

# Now use Byaldi normally with the new method
RAG = RAGMultiModalModel.from_index("my_index")
query_image = Image.open("query.png")
results = RAG.search_by_image(query_image, k=5)
```

### Option 3: Wrapper Class

```python
from byaldi_extensions import ExtendedRAGMultiModalModel
from PIL import Image

# Use the extended wrapper class
RAG = ExtendedRAGMultiModalModel.from_index("my_index")

# All original methods work
text_results = RAG.search("query text", k=5)

# Plus the new search_by_image method
query_image = Image.open("query.png")
image_results = RAG.search_by_image(query_image, k=5)
```

## Parameters

- **image** (PIL.Image.Image): The PIL image to search with
- **k** (int): The number of similar results to return. Default is 10. Use k=-1 to return all pages.
- **filter_metadata** (Optional[Dict[str, str]]): Optional metadata filter to narrow down search
- **return_base64_results** (Optional[bool]): Whether to return base64-encoded images in results

## Example: Complete Workflow

```python
from byaldi import RAGMultiModalModel
from byaldi_extensions import search_by_image
from PIL import Image

# 1. Load or create an index
RAG = RAGMultiModalModel.from_pretrained("vidore/colpali-v1.2")
RAG.index(
    input_path="documents/",
    index_name="my_docs",
    store_collection_with_index=True
)

# 2. Load a query image (could be a screenshot, photo, diagram, etc.)
query_image = Image.open("reference_diagram.png")

# 3. Search for similar images
results = search_by_image(RAG, query_image, k=10)

# 4. Process results
for i, result in enumerate(results, 1):
    print(f"{i}. Document: {result.doc_id}, Page: {result.page_num}")
    print(f"   Similarity Score: {result.score:.4f}")
    if result.metadata:
        print(f"   Metadata: {result.metadata}")
    print()
```

## Use Cases

1. **Visual Duplicate Detection**: Find duplicate or near-duplicate images in your document collection
2. **Similar Layout Search**: Find pages with similar visual layouts or structures
3. **Diagram Matching**: Search for similar diagrams, charts, or infographics
4. **Screenshot Search**: Find documents containing similar screenshots or UI elements
5. **Visual Content Discovery**: Explore visually similar content across your document corpus

## Combining with Other Search Methods

You can combine `search_by_image` with other search methods:

```python
from byaldi_extensions import ExtendedRAGMultiModalModel
from PIL import Image

RAG = ExtendedRAGMultiModalModel.from_index("my_index")

# Text-based search
text_results = RAG.search("machine learning", k=5)

# Image-based search
query_image = Image.open("ml_diagram.png")
image_results = RAG.search_by_image(query_image, k=5)

# Page-based search (find similar pages to a specific page)
page_results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
```

## Notes

- The image will be processed using the same model that was used to index your documents
- The search is performed against all indexed page embeddings
- Results are ranked by similarity score (higher is more similar)
- The function works with any PIL-compatible image format (PNG, JPEG, etc.)
