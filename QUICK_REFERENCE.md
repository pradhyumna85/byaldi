# Quick Reference: search_by_page Without Modifying Byaldi

## 🚀 Three Ways to Use

### 1️⃣ Standalone Function (Copy-Paste Ready)
```python
from byaldi import RAGMultiModalModel
from byaldi_extensions import search_by_page

RAG = RAGMultiModalModel.from_index("my_index")
results = search_by_page(RAG, doc_id=0, page_num=3, k=5)
```

### 2️⃣ Monkey Patch (One-Line Setup)
```python
from byaldi_extensions import patch_search_by_page; patch_search_by_patch()
from byaldi import RAGMultiModalModel

RAG = RAGMultiModalModel.from_index("my_index")
results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
```

### 3️⃣ Wrapper Class (Production Ready)
```python
from byaldi_extensions import ExtendedRAGMultiModalModel

RAG = ExtendedRAGMultiModalModel.from_index("my_index")
results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
```

## 📋 Parameters

```python
search_by_page(
    model_or_self,           # RAGMultiModalModel instance
    doc_id=0,                # Document ID (int)
    page_num=3,              # Page number, 1-indexed (int)
    k=5,                     # Number of results (int)
    filter_metadata=None,    # Optional: {"key": "value"}
    return_base64_results=None  # Optional: True/False
)
```

## 📊 Result Format

```python
for result in results:
    result.doc_id       # Document ID
    result.page_num     # Page number (1-indexed)
    result.score        # Similarity score (higher = more similar)
    result.metadata     # Document metadata dict
    result.base64       # Base64 image (if requested)
```

## 🎯 Common Use Cases

### Find Similar Pages
```python
similar = RAG.search_by_page(doc_id=0, page_num=5, k=10)
```

### Filter by Metadata
```python
similar = RAG.search_by_page(
    doc_id=0, page_num=5, k=10,
    filter_metadata={"category": "technical"}
)
```

### Get Images
```python
similar = RAG.search_by_page(
    doc_id=0, page_num=5, k=10,
    return_base64_results=True
)
```

### Cross-Document Similarity
```python
results = RAG.search_by_page(doc_id=0, page_num=5, k=10)
other_docs = [r for r in results if r.doc_id != 0]
```

## 🔧 Installation

```bash
# Just copy the file to your project
cp byaldi_extensions.py /path/to/your/project/

# Or download
wget https://raw.githubusercontent.com/.../byaldi_extensions.py
```

## ⚡ Which Method to Choose?

| Need | Use |
|------|-----|
| Maximum safety | Standalone Function |
| Best developer experience | Monkey Patch |
| Production deployment | Wrapper Class |
| Quick script | Standalone Function |
| Jupyter notebook | Monkey Patch |
| Library/package | Wrapper Class |

## 🐛 Troubleshooting

### Import Error
```python
import sys
sys.path.insert(0, '/path/to/directory')
from byaldi_extensions import search_by_page
```

### Page Not Found
```python
# Check what pages exist
print(RAG.model.embed_id_to_doc_id)
```

### Patch Not Working
```python
# Patch BEFORE importing Byaldi
from byaldi_extensions import patch_search_by_page
patch_search_by_page()
from byaldi import RAGMultiModalModel  # Import after patch
```

## 📚 More Info

- `EXTENSIONS_README.md` - Full documentation
- `examples_extensions.py` - Complete examples
- `EXTENSIONS_SUMMARY.md` - Detailed summary
- `test_extensions.py` - Test suite

## ✅ Compatibility

- ✅ All Byaldi versions
- ✅ ColPali, ColQwen2, ColSmol
- ✅ Existing indexes
- ✅ No package modifications
- ✅ Zero performance overhead

## 🎉 That's It!

Copy `byaldi_extensions.py` to your project and start finding similar pages without modifying any Byaldi code!
