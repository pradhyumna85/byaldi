"""
Example script demonstrating how to find similar pages to an existing page in a Byaldi index.

This script shows how to:
1. Load an existing index
2. Use search_by_page() to find pages similar to a specific page (doc_id, page_num)
"""

from byaldi import RAGMultiModalModel

# Load an existing index
# Replace "your_index_name" with the name of your index
RAG = RAGMultiModalModel.from_index("your_index_name")

# Find the top 5 pages most similar to page 3 of document 0
doc_id = 0
page_num = 3
k = 5

results = RAG.search_by_page(doc_id=doc_id, page_num=page_num, k=k)

# Display results
print(f"Top {k} pages similar to doc_id={doc_id}, page_num={page_num}:")
print("-" * 80)

for i, result in enumerate(results, 1):
    print(f"{i}. Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score:.4f}")
    if result.metadata:
        print(f"   Metadata: {result.metadata}")
    print()

# You can also use optional parameters:
# - filter_metadata: Filter results by metadata
# - return_base64_results: Return base64-encoded images (if stored with index)

# Example with metadata filter:
# results = RAG.search_by_page(
#     doc_id=0,
#     page_num=3,
#     k=5,
#     filter_metadata={"author": "John Doe"}
# )
