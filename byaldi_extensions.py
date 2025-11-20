"""
Byaldi Extensions - Add search_by_page functionality without modifying the package.

This module provides a way to add the search_by_page functionality to existing
Byaldi installations through monkey-patching or wrapper classes.

Usage Option 1 - Monkey Patch (modifies the class):
    from byaldi_extensions import patch_search_by_page
    patch_search_by_page()
    
    # Now use Byaldi normally
    from byaldi import RAGMultiModalModel
    RAG = RAGMultiModalModel.from_index("my_index")
    results = RAG.search_by_page(doc_id=0, page_num=3, k=5)

Usage Option 2 - Wrapper Class (no modification):
    from byaldi_extensions import ExtendedRAGMultiModalModel
    
    RAG = ExtendedRAGMultiModalModel.from_index("my_index")
    results = RAG.search_by_page(doc_id=0, page_num=3, k=5)

Usage Option 3 - Standalone Function:
    from byaldi import RAGMultiModalModel
    from byaldi_extensions import search_by_page
    
    RAG = RAGMultiModalModel.from_index("my_index")
    results = search_by_page(RAG, doc_id=0, page_num=3, k=5)
"""

from typing import Dict, List, Optional, Union
from pathlib import Path


def search_by_page_impl(
    model_instance,
    doc_id: int,
    page_num: int,
    k: int = 10,
    filter_metadata: Optional[Dict[str, str]] = None,
    return_base64_results: Optional[bool] = None,
):
    """
    Implementation of search_by_page that works with any Byaldi model instance.
    
    This function can be used standalone or as a monkey-patch.
    
    Parameters:
        model_instance: The RAGMultiModalModel or ColPaliModel instance
        doc_id (int): The document ID of the reference page
        page_num (int): The page number of the reference page (1-indexed)
        k (int): The number of similar results to return. Default is 10. Use k=-1 to return all pages.
        filter_metadata (Optional[Dict[str, str]]): Optional metadata filter
        return_base64_results (Optional[bool]): Whether to return base64 images
    
    Returns:
        List[Result]: A list of Result objects representing the most similar pages
    """
    # Import here to avoid issues if byaldi is not installed
    from byaldi.objects import Result
    
    # Get the ColPaliModel wrapper (not the PyTorch model)
    # RAGMultiModalModel.model -> ColPaliModel (has indexed_embeddings, embed_id_to_doc_id, etc.)
    # ColPaliModel.model -> PyTorch model (ColPali/ColQwen2/ColIdefics3)
    if hasattr(model_instance, 'model') and hasattr(model_instance.model, 'indexed_embeddings'):
        # This is RAGMultiModalModel, get the ColPaliModel wrapper
        colpali_model = model_instance.model
    elif hasattr(model_instance, 'indexed_embeddings'):
        # This is already the ColPaliModel wrapper
        colpali_model = model_instance
    else:
        raise ValueError(
            "model_instance must be a RAGMultiModalModel or ColPaliModel instance"
        )
    
    # Set default value for return_base64_results if not provided
    if return_base64_results is None:
        return_base64_results = bool(getattr(colpali_model, 'collection', {}))
    
    # Find the embedding ID for the given doc_id and page_num
    embed_id = None
    for eid, doc_info in colpali_model.embed_id_to_doc_id.items():
        if doc_info["doc_id"] == doc_id and doc_info["page_id"] == page_num:
            embed_id = eid
            break
    
    if embed_id is None:
        raise ValueError(
            f"Page not found in index: doc_id={doc_id}, page_num={page_num}"
        )
    
    # Get the embedding for this page
    page_embedding = colpali_model.indexed_embeddings[embed_id]
    
    # Prepare embeddings for scoring
    if filter_metadata:
        req_embeddings, req_embedding_ids = colpali_model.filter_embeddings(
            filter_metadata=filter_metadata
        )
    else:
        req_embeddings = colpali_model.indexed_embeddings
        req_embedding_ids = None
    
    # Handle k=-1 to return all pages
    if k == -1:
        k_actual = len(req_embeddings)
    else:
        # Request k+1 results since we'll exclude the query page itself
        # This ensures we return exactly k results after exclusion
        k_actual = min(k + 1, len(req_embeddings))
    
    # Compute scores using the page embedding
    qs = [page_embedding]
    scores = colpali_model.processor.score(qs, req_embeddings).cpu().numpy()
    
    # Get top k_actual relevant pages
    top_pages = scores.argsort(axis=1)[0][-k_actual:][::-1].tolist()
    
    # Create Result objects
    query_results = []
    for idx in top_pages:
        if filter_metadata:
            adjusted_embed_id = req_embedding_ids[idx]
        else:
            adjusted_embed_id = int(idx)
        
        # Skip the query page itself
        if adjusted_embed_id == embed_id:
            continue
        
        # Stop if we've collected enough results (only matters when k != -1)
        if k != -1 and len(query_results) >= k:
            break
        
        doc_info = colpali_model.embed_id_to_doc_id[adjusted_embed_id]
        result = Result(
            doc_id=doc_info["doc_id"],
            page_num=int(doc_info["page_id"]),
            score=float(scores[0][int(idx)]),
            metadata=getattr(colpali_model, 'doc_id_to_metadata', {}).get(int(doc_info["doc_id"]), {}),
            base64=getattr(colpali_model, 'collection', {}).get(adjusted_embed_id)
            if return_base64_results
            else None,
        )
        query_results.append(result)
    
    return query_results


def search_by_page(
    model_instance,
    doc_id: int,
    page_num: int,
    k: int = 10,
    filter_metadata: Optional[Dict[str, str]] = None,
    return_base64_results: Optional[bool] = None,
):
    """
    Standalone function to find similar pages in a Byaldi index.
    
    Usage:
        from byaldi import RAGMultiModalModel
        from byaldi_extensions import search_by_page
        
        RAG = RAGMultiModalModel.from_index("my_index")
        results = search_by_page(RAG, doc_id=0, page_num=3, k=5)
    
    Parameters:
        model_instance: The RAGMultiModalModel instance
        doc_id (int): The document ID of the reference page
        page_num (int): The page number of the reference page (1-indexed)
        k (int): The number of similar results to return. Default is 10. Use k=-1 to return all pages.
        filter_metadata (Optional[Dict[str, str]]): Optional metadata filter
        return_base64_results (Optional[bool]): Whether to return base64 images
    
    Returns:
        List[Result]: A list of Result objects representing the most similar pages
    """
    return search_by_page_impl(
        model_instance, doc_id, page_num, k, filter_metadata, return_base64_results
    )


def patch_search_by_page():
    """
    Monkey-patch the Byaldi classes to add search_by_page method.
    
    This modifies the RAGMultiModalModel and ColPaliModel classes in-place.
    Call this once at the start of your script before using Byaldi.
    
    Usage:
        from byaldi_extensions import patch_search_by_page
        patch_search_by_page()
        
        # Now use Byaldi normally with the new method
        from byaldi import RAGMultiModalModel
        RAG = RAGMultiModalModel.from_index("my_index")
        results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
    """
    try:
        from byaldi import RAGMultiModalModel
        from byaldi.colpali import ColPaliModel
        
        # Add method to ColPaliModel
        ColPaliModel.search_by_page = search_by_page_impl
        
        # Add method to RAGMultiModalModel
        def rag_search_by_page(
            self,
            doc_id: int,
            page_num: int,
            k: int = 10,
            filter_metadata: Optional[Dict[str, str]] = None,
            return_base64_results: Optional[bool] = None,
        ):
            return self.model.search_by_page(
                doc_id, page_num, k, filter_metadata, return_base64_results
            )
        
        RAGMultiModalModel.search_by_page = rag_search_by_page
        
        print("✓ Successfully patched Byaldi with search_by_page functionality")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to patch Byaldi: {e}")
        return False


class ExtendedRAGMultiModalModel:
    """
    Wrapper class that extends RAGMultiModalModel with search_by_page functionality.
    
    This doesn't modify the original Byaldi code, but wraps it to add new methods.
    Use this if you want to avoid monkey-patching.
    
    Usage:
        from byaldi_extensions import ExtendedRAGMultiModalModel
        
        # Use exactly like RAGMultiModalModel
        RAG = ExtendedRAGMultiModalModel.from_index("my_index")
        
        # All original methods work
        results = RAG.search("query", k=5)
        
        # Plus the new method
        results = RAG.search_by_page(doc_id=0, page_num=3, k=5)
    """
    
    def __init__(self, base_model):
        """Initialize with a RAGMultiModalModel instance."""
        self._base_model = base_model
        self.model = base_model.model
    
    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path: Union[str, Path],
        index_root: str = ".byaldi",
        device: str = "cuda",
        verbose: int = 1,
    ):
        """Load a model from pretrained checkpoint."""
        from byaldi import RAGMultiModalModel
        base_model = RAGMultiModalModel.from_pretrained(
            pretrained_model_name_or_path, index_root, device, verbose
        )
        return cls(base_model)
    
    @classmethod
    def from_index(
        cls,
        index_path: Union[str, Path],
        index_root: str = ".byaldi",
        device: str = "cuda",
        verbose: int = 1,
    ):
        """Load a model and index."""
        from byaldi import RAGMultiModalModel
        base_model = RAGMultiModalModel.from_index(
            index_path, index_root, device, verbose
        )
        return cls(base_model)
    
    def index(self, *args, **kwargs):
        """Delegate to base model."""
        return self._base_model.index(*args, **kwargs)
    
    def add_to_index(self, *args, **kwargs):
        """Delegate to base model."""
        return self._base_model.add_to_index(*args, **kwargs)
    
    def search(self, *args, **kwargs):
        """Delegate to base model."""
        return self._base_model.search(*args, **kwargs)
    
    def search_by_page(
        self,
        doc_id: int,
        page_num: int,
        k: int = 10,
        filter_metadata: Optional[Dict[str, str]] = None,
        return_base64_results: Optional[bool] = None,
    ):
        """
        Find the most similar pages to a given page in the index.
        
        Parameters:
            doc_id (int): The document ID of the reference page
            page_num (int): The page number of the reference page (1-indexed)
            k (int): The number of similar results to return. Default is 10. Use k=-1 to return all pages.
            filter_metadata (Optional[Dict[str, str]]): Optional metadata filter
            return_base64_results (Optional[bool]): Whether to return base64 images
        
        Returns:
            List[Result]: A list of Result objects representing the most similar pages
        """
        return search_by_page_impl(
            self._base_model, doc_id, page_num, k, filter_metadata, return_base64_results
        )
    
    def get_doc_ids_to_file_names(self):
        """Delegate to base model."""
        return self._base_model.get_doc_ids_to_file_names()
    
    def as_langchain_retriever(self, **kwargs):
        """Delegate to base model."""
        return self._base_model.as_langchain_retriever(**kwargs)
    
    def __getattr__(self, name):
        """Delegate any other attributes to the base model."""
        return getattr(self._base_model, name)


# Convenience: Auto-patch on import if BYALDI_AUTO_PATCH env var is set
import os
if os.environ.get("BYALDI_AUTO_PATCH", "").lower() in ("1", "true", "yes"):
    patch_search_by_page()
