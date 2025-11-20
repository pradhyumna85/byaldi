from pathlib import Path
from typing import Generator

import pytest
from colpali_engine.utils.torch_utils import get_torch_device, tear_down_torch

from byaldi import RAGMultiModalModel

path_document_1 = Path("docs/attention.pdf")
path_document_2 = Path("docs/attention_copy.pdf")


@pytest.fixture(scope="function")
def rag_model_from_pretrained() -> Generator[RAGMultiModalModel, None, None]:
    device = get_torch_device("auto")
    print(f"Using device: {device}")
    yield RAGMultiModalModel.from_pretrained("vidore/colpali-v1.2", device=device)
    tear_down_torch()


@pytest.fixture(scope="function")
def rag_model_from_index() -> Generator[RAGMultiModalModel, None, None]:
    yield RAGMultiModalModel.from_index("multi_doc_index")
    tear_down_torch()


@pytest.mark.slow
def test_single_pdf(rag_model_from_pretrained: RAGMultiModalModel):
    if not Path("docs/attention.pdf").is_file():
        raise FileNotFoundError(
            f"Please download the PDF file from https://arxiv.org/pdf/1706.03762 and move it to {path_document_1}."
        )

    # Index a single PDF
    rag_model_from_pretrained.index(
        input_path="docs/attention.pdf",
        index_name="attention_index",
        store_collection_with_index=True,
        overwrite=True,
    )

    # Test retrieval
    queries = [
        "How does the positional encoding thing work?",
        "what's the BLEU score of this new strange method?",
    ]

    for query in queries:
        results = rag_model_from_pretrained.search(query, k=3)

        print(f"\nQuery: {query}")
        for result in results:
            print(
                f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score}"
            )

        # Check if the expected page (6 for positional encoding) is in the top results
        if "positional encoding" in query.lower():
            assert any(
                r.page_num == 6 for r in results
            ), "Expected page 6 for positional encoding query"

        # Check if the expected pages (8 and 9 for BLEU score) are in the top results
        if "bleu score" in query.lower():
            assert any(
                r.page_num in [8, 9] for r in results
            ), "Expected pages 8 or 9 for BLEU score query"


@pytest.mark.slow
def test_multi_document(rag_model_from_pretrained: RAGMultiModalModel):
    if not Path("docs/attention.pdf").is_file():
        raise FileNotFoundError(
            f"Please download the PDF file from https://arxiv.org/pdf/1706.03762 and move it to {path_document_1}."
        )
    if not Path("docs/attention_copy.pdf").is_file():
        raise FileNotFoundError(
            f"Please download the PDF file from https://arxiv.org/pdf/1706.03762 and move it to {path_document_2}."
        )

    # Index a directory of documents
    rag_model_from_pretrained.index(
        input_path="docs/",
        index_name="multi_doc_index",
        store_collection_with_index=True,
        overwrite=True,
    )

    # Test retrieval
    queries = [
        "How does the positional encoding thing work?",
        "what's the BLEU score of this new strange method?",
    ]

    for query in queries:
        results = rag_model_from_pretrained.search(query, k=5)

        print(f"\nQuery: {query}")
        for result in results:
            print(
                f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score}"
            )

        # Check if the expected page (6 for positional encoding) is in the top results
        if "positional encoding" in query.lower():
            assert any(
                r.page_num == 6 for r in results
            ), "Expected page 6 for positional encoding query"

        # Check if the expected pages (8 and 9 for BLEU score) are in the top results
        if "bleu score" in query.lower():
            assert any(
                r.page_num in [8, 9] for r in results
            ), "Expected pages 8 or 9 for BLEU score query"


@pytest.mark.slow
def test_search_by_page(rag_model_from_pretrained: RAGMultiModalModel):
    if not Path("docs/attention.pdf").is_file():
        raise FileNotFoundError(
            f"Please download the PDF file from https://arxiv.org/pdf/1706.03762 and move it to {path_document_1}."
        )

    # Index a single PDF
    rag_model_from_pretrained.index(
        input_path="docs/attention.pdf",
        index_name="attention_index_search_by_page",
        store_collection_with_index=True,
        overwrite=True,
    )

    # Test search_by_page: find pages similar to page 6 (positional encoding)
    doc_id = 0
    page_num = 6
    k = 5

    results = rag_model_from_pretrained.search_by_page(
        doc_id=doc_id, page_num=page_num, k=k
    )

    print(f"\nPages similar to doc_id={doc_id}, page_num={page_num}:")
    for result in results:
        print(
            f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score}"
        )

    # Verify we got results
    assert len(results) > 0, "Expected at least one similar page"
    
    # Verify the query page itself is not in the results
    assert not any(
        r.doc_id == doc_id and r.page_num == page_num for r in results
    ), "Query page should not be in results"
    
    # Verify all results have valid scores
    assert all(r.score > 0 for r in results), "All results should have positive scores"


@pytest.mark.skip("This test should be made independent of the previous tests.")
@pytest.mark.slow
def test_add_to_index(rag_model_from_index: RAGMultiModalModel):
    # NOTE: This test should run after the test_multi_document test.

    # Add a new document to the index
    rag_model_from_index.add_to_index(
        input_item="docs/",
        store_collection_with_index=True,
        doc_id=[1002, 1003],
        metadata=[{"author": "John Doe", "year": 2023}] * 2,
    )

    # Test retrieval with the updated index
    queries = ["what's the BLEU score of this new strange method?"]

    for query in queries:
        results = rag_model_from_index.search(query, k=3)

        print(f"\nQuery: {query}")
        for result in results:
            print(
                f"Doc ID: {result.doc_id}, Page: {result.page_num}, Score: {result.score}"
            )
            print(f"Metadata: {result.metadata}")

        # Check if the expected page (6 for positional encoding) is in the top results
        if "positional encoding" in query.lower():
            assert any(
                r.page_num == 6 for r in results
            ), "Expected page 6 for positional encoding query"

        # Check if the expected pages (8 and 9 for BLEU score) are in the top results
        if "bleu score" in query.lower():
            assert any(
                r.page_num in [8, 9] for r in results
            ), "Expected pages 8 or 9 for BLEU score query"
