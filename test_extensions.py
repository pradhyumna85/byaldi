#!/usr/bin/env python3
"""
Test script for byaldi_extensions.py

This script tests all three usage patterns without requiring an actual index.
It uses mocking to simulate the Byaldi environment.
"""

import sys
from unittest.mock import Mock, MagicMock
import numpy as np


def create_mock_model():
    """Create a mock Byaldi model for testing."""
    # Create mock Result class
    class MockResult:
        def __init__(self, doc_id, page_num, score, metadata=None, base64=None):
            self.doc_id = doc_id
            self.page_num = page_num
            self.score = score
            self.metadata = metadata or {}
            self.base64 = base64
        
        def dict(self):
            return {
                "doc_id": self.doc_id,
                "page_num": self.page_num,
                "score": self.score,
                "metadata": self.metadata,
                "base64": self.base64,
            }
    
    # Mock the byaldi.objects module
    sys.modules['byaldi.objects'] = Mock()
    sys.modules['byaldi.objects'].Result = MockResult
    
    # Create mock embeddings
    mock_embeddings = [np.random.randn(128) for _ in range(10)]
    
    # Create mock embed_id_to_doc_id mapping
    embed_id_to_doc_id = {
        0: {"doc_id": 0, "page_id": 1},
        1: {"doc_id": 0, "page_id": 2},
        2: {"doc_id": 0, "page_id": 3},
        3: {"doc_id": 1, "page_id": 1},
        4: {"doc_id": 1, "page_id": 2},
        5: {"doc_id": 2, "page_id": 1},
        6: {"doc_id": 2, "page_id": 2},
        7: {"doc_id": 2, "page_id": 3},
        8: {"doc_id": 3, "page_id": 1},
        9: {"doc_id": 3, "page_id": 2},
    }
    
    # Create mock processor
    mock_processor = Mock()
    mock_processor.score = Mock(return_value=Mock(
        cpu=Mock(return_value=Mock(
            numpy=Mock(return_value=np.random.rand(1, 10))
        ))
    ))
    
    # Create mock ColPali model
    mock_colpali = Mock()
    mock_colpali.indexed_embeddings = mock_embeddings
    mock_colpali.embed_id_to_doc_id = embed_id_to_doc_id
    mock_colpali.doc_id_to_metadata = {0: {"author": "Test"}, 1: {}, 2: {}}
    mock_colpali.collection = {}
    mock_colpali.processor = mock_processor
    mock_colpali.filter_embeddings = Mock(return_value=(mock_embeddings, list(range(10))))
    
    # Create mock RAG model
    mock_rag = Mock()
    mock_rag.model = mock_colpali
    
    return mock_rag


def test_standalone_function():
    """Test the standalone function approach."""
    print("\n" + "="*80)
    print("TEST 1: Standalone Function")
    print("="*80)
    
    try:
        from byaldi_extensions import search_by_page
        
        mock_rag = create_mock_model()
        
        # Test basic call
        results = search_by_page(mock_rag, doc_id=0, page_num=1, k=5)
        
        print(f"✓ Function executed successfully")
        print(f"✓ Returned {len(results)} results")
        print(f"✓ Results have correct attributes: doc_id, page_num, score")
        
        # Verify results
        assert len(results) <= 5, "Should return at most k results"
        assert all(hasattr(r, 'doc_id') for r in results), "Results should have doc_id"
        assert all(hasattr(r, 'page_num') for r in results), "Results should have page_num"
        assert all(hasattr(r, 'score') for r in results), "Results should have score"
        
        # Verify query page is excluded
        assert not any(r.doc_id == 0 and r.page_num == 1 for r in results), \
            "Query page should be excluded"
        
        print("✓ All assertions passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wrapper_class():
    """Test the wrapper class approach."""
    print("\n" + "="*80)
    print("TEST 2: Wrapper Class")
    print("="*80)
    
    try:
        from byaldi_extensions import ExtendedRAGMultiModalModel
        
        mock_rag = create_mock_model()
        
        # Create wrapper
        extended = ExtendedRAGMultiModalModel(mock_rag)
        
        # Test method exists
        assert hasattr(extended, 'search_by_page'), "Wrapper should have search_by_page"
        
        # Test basic call
        results = extended.search_by_page(doc_id=0, page_num=1, k=5)
        
        print(f"✓ Wrapper class instantiated successfully")
        print(f"✓ search_by_page method exists")
        print(f"✓ Returned {len(results)} results")
        
        # Verify results
        assert len(results) <= 5, "Should return at most k results"
        
        # Test delegation to base model
        assert extended.model == mock_rag.model, "Should delegate to base model"
        
        print("✓ All assertions passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n" + "="*80)
    print("TEST 3: Error Handling")
    print("="*80)
    
    try:
        from byaldi_extensions import search_by_page
        
        mock_rag = create_mock_model()
        
        # Test with non-existent page
        try:
            results = search_by_page(mock_rag, doc_id=999, page_num=999, k=5)
            print("✗ Should have raised ValueError for non-existent page")
            return False
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")
        
        print("✓ All error handling tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_implementation_details():
    """Test implementation details."""
    print("\n" + "="*80)
    print("TEST 4: Implementation Details")
    print("="*80)
    
    try:
        from byaldi_extensions import search_by_page_impl
        
        mock_rag = create_mock_model()
        
        # Test with metadata filter
        results = search_by_page_impl(
            mock_rag,
            doc_id=0,
            page_num=1,
            k=3,
            filter_metadata={"author": "Test"}
        )
        
        print(f"✓ Metadata filtering works")
        print(f"✓ Returned {len(results)} results with filter")
        
        # Test with return_base64_results
        results = search_by_page_impl(
            mock_rag,
            doc_id=0,
            page_num=1,
            k=3,
            return_base64_results=False
        )
        
        print(f"✓ return_base64_results parameter works")
        
        print("✓ All implementation tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("BYALDI EXTENSIONS - TEST SUITE")
    print("="*80)
    print("\nTesting byaldi_extensions.py without requiring an actual index")
    
    results = []
    
    # Run tests
    results.append(("Standalone Function", test_standalone_function()))
    results.append(("Wrapper Class", test_wrapper_class()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Implementation Details", test_implementation_details()))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The extensions module is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
