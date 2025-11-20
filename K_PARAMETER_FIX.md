# K Parameter Fix: Return Exact Number of Results

## Problem

When calling `search_by_page(doc_id=0, page_num=12, k=5)`, only **4 results** were returned instead of 5.

## Root Cause

The function automatically excludes the query page itself from results (so you don't get page 12 as similar to page 12). However, the original code was:

1. Requesting top `k` pages
2. Then filtering out the query page
3. Resulting in `k-1` results

**Example:**
```python
results = RAG.search_by_page(doc_id=0, page_num=12, k=5)
# Expected: 5 results
# Got: 4 results (because page 12 was excluded)
```

## Solution

### Fix 1: Request k+1 Results

Now the function requests `k+1` results to account for the excluded query page:

```python
# Request k+1 results since we'll exclude the query page itself
# This ensures we return exactly k results after exclusion
k_actual = min(k + 1, len(req_embeddings))
```

Then it stops collecting results once it has exactly `k` results:

```python
# Stop if we've collected enough results
if k != -1 and len(query_results) >= k:
    break
```

### Fix 2: Support k=-1 for All Pages

Added support for `k=-1` to return **all similar pages** in the index:

```python
# Handle k=-1 to return all pages
if k == -1:
    k_actual = len(req_embeddings)
else:
    k_actual = min(k + 1, len(req_embeddings))
```

## Usage

### Get Exactly 5 Results
```python
results = RAG.search_by_page(doc_id=0, page_num=12, k=5)
print(len(results))  # Now returns 5 (not 4!)
```

### Get All Similar Pages
```python
# Return all pages sorted by similarity
results = RAG.search_by_page(doc_id=0, page_num=12, k=-1)
print(len(results))  # Returns all pages in index (excluding page 12)
```

### Examples

```python
from byaldi_extensions import patch_search_by_page
patch_search_by_page()

from byaldi import RAGMultiModalModel
RAG = RAGMultiModalModel.from_index("my_index")

# Get exactly 5 similar pages
results = RAG.search_by_page(doc_id=0, page_num=12, k=5)
assert len(results) == 5  # ✅ Now works!

# Get top 10 similar pages
results = RAG.search_by_page(doc_id=0, page_num=12, k=10)
assert len(results) == 10  # ✅ Exactly 10

# Get ALL similar pages
results = RAG.search_by_page(doc_id=0, page_num=12, k=-1)
print(f"Found {len(results)} total pages")  # All pages except page 12

# With metadata filter
results = RAG.search_by_page(
    doc_id=0, 
    page_num=12, 
    k=-1,
    filter_metadata={"category": "technical"}
)
print(f"Found {len(results)} technical pages")
```

## Changes Made

**Lines 103-109**: Added logic to handle k=-1 and request k+1 results
```python
# Handle k=-1 to return all pages
if k == -1:
    k_actual = len(req_embeddings)
else:
    # Request k+1 results since we'll exclude the query page itself
    k_actual = min(k + 1, len(req_embeddings))
```

**Lines 130-132**: Added early stopping to ensure exactly k results
```python
# Stop if we've collected enough results (only matters when k != -1)
if k != -1 and len(query_results) >= k:
    break
```

**Documentation**: Updated all docstrings to mention k=-1 support

## Impact

✅ **Fixed**: Now returns exactly `k` results as expected  
✅ **New feature**: `k=-1` returns all pages  
✅ **No breaking changes**: Existing code works better  
✅ **Query page always excluded**: Page 12 never appears when searching for similar pages to page 12  

## Testing

```python
# Test 1: Exact k results
results = RAG.search_by_page(doc_id=0, page_num=12, k=5)
assert len(results) == 5, f"Expected 5, got {len(results)}"

# Test 2: k=-1 returns all
results = RAG.search_by_page(doc_id=0, page_num=12, k=-1)
assert len(results) == total_pages - 1  # All except query page

# Test 3: Query page not in results
results = RAG.search_by_page(doc_id=0, page_num=12, k=10)
assert not any(r.doc_id == 0 and r.page_num == 12 for r in results)

# Test 4: Results are sorted by score
results = RAG.search_by_page(doc_id=0, page_num=12, k=10)
scores = [r.score for r in results]
assert scores == sorted(scores, reverse=True)
```

## Version

This fix is included in the latest version of `byaldi_extensions.py`.
