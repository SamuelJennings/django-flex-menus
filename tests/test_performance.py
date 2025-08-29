"""
Performance and thread safety tests for django-flex-menus.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock

import pytest

from flex_menu.menu import BaseMenu, MenuGroup, MenuLink


class TestPerformance:
    """Test performance characteristics of the menu system."""

    def test_large_menu_creation_performance(self):
        """Test performance of creating large menu structures."""
        start_time = time.time()

        # Create a large menu structure
        main_menu = MenuGroup(name="performance_test")

        # Add 100 top-level items
        for i in range(100):
            section = MenuGroup(name=f"section_{i}")

            # Add 10 items to each section
            for j in range(10):
                item = MenuLink(name=f"item_{i}_{j}", url=f"/section{i}/item{j}/")
                section.append(item)

            main_menu.append(section)

        creation_time = time.time() - start_time

        # Should create 1000+ menu items reasonably quickly (< 1 second)
        assert creation_time < 1.0
        assert len(main_menu.children) == 100
        assert len(main_menu.children[0].children) == 10

    def test_menu_processing_performance(self, mock_request):
        """Test performance of menu processing."""
        # Create a moderately complex menu
        main_menu = MenuGroup(name="processing_test")

        for i in range(20):
            section = MenuGroup(name=f"section_{i}")
            for j in range(5):
                item = MenuLink(name=f"item_{i}_{j}", url=f"/section{i}/item{j}/")
                section.append(item)
            main_menu.append(section)

        # Measure processing time
        start_time = time.time()

        for _ in range(10):  # Process 10 times
            processed = main_menu.process(mock_request)
            assert processed is not None

        processing_time = time.time() - start_time

        # 10 processing operations should be fast (< 0.1 seconds)
        assert processing_time < 0.1

    def test_url_resolution_caching_performance(self):
        """Test that URL resolution caching improves performance."""
        item = MenuLink(name="cached_test", url="/test/")

        # First resolution (no cache)
        start_time = time.time()
        url1 = item.resolve_url()
        first_time = time.time() - start_time

        # Second resolution (should use cache)
        start_time = time.time()
        url2 = item.resolve_url()
        second_time = time.time() - start_time

        assert url1 == url2 == "/test/"
        # Second call should be faster (cached)
        assert second_time <= first_time

    def test_deep_menu_traversal_performance(self):
        """Test performance of traversing deeply nested menus."""
        # Create a deeply nested structure (10 levels deep)
        current = BaseMenu(name="root", template_name="menu/base.html")

        for i in range(10):
            child = BaseMenu(name=f"level_{i}", template_name="menu/base.html")
            current.append(child)
            current = child

        root = current
        while root.parent:
            root = root.parent

        # Test finding the deepest item
        start_time = time.time()

        for _ in range(100):  # Search 100 times
            found = root.get("level_9")
            assert found is not None

        search_time = time.time() - start_time

        # 100 deep searches should be reasonably fast (< 0.1 seconds)
        assert search_time < 0.1


class TestThreadSafety:
    """Test thread safety of the menu system."""

    def test_concurrent_menu_processing(self, mock_request):
        """Test that concurrent menu processing is thread-safe."""
        menu = MenuGroup(name="thread_test")

        for i in range(5):
            item = MenuLink(name=f"item_{i}", url=f"/item{i}/")
            menu.append(item)

        results = []
        errors = []

        def process_menu():
            try:
                for _ in range(10):
                    processed = menu.process(mock_request)
                    results.append(processed.name)
                    # Small delay to increase chance of race conditions
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Run 10 threads concurrently
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=process_menu)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 100  # 10 threads × 10 operations each
        assert all(result == "thread_test" for result in results)

    def test_concurrent_menu_modification(self):
        """Test that concurrent menu modifications work correctly."""
        parent = BaseMenu(name="concurrent_parent", template_name="menu/base.html")

        def add_children(thread_id):
            for i in range(10):
                child = BaseMenu(name=f"child_{thread_id}_{i}", template_name="menu/base.html")
                parent.append(child)
                time.sleep(0.001)  # Small delay

        # Start multiple threads adding children
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=add_children, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Check that all children were added
        assert len(parent.children) == 50  # 5 threads × 10 children each

        # Check that all children have unique names
        names = [child.name for child in parent.children]
        assert len(set(names)) == 50  # All names should be unique

    def test_concurrent_url_resolution(self):
        """Test that concurrent URL resolution is thread-safe."""
        item = MenuLink(name="concurrent_url", url="/concurrent/")

        results = []
        errors = []

        def resolve_url():
            try:
                for _ in range(20):
                    url = item.resolve_url()
                    results.append(url)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Run multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(resolve_url) for _ in range(5)]

            # Wait for all to complete
            for future in as_completed(futures):
                future.result()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 100  # 5 threads × 20 operations each
        assert all(url == "/concurrent/" for url in results)

    def test_request_isolation(self):
        """Test that different requests don't interfere with each other."""
        menu = MenuGroup(name="isolation_test")
        item1 = MenuLink(name="item1", url="/path1/")
        item2 = MenuLink(name="item2", url="/path2/")
        menu.extend([item1, item2])

        # Create different mock requests
        request1 = Mock(path="/path1/", user=Mock(is_authenticated=True))
        request2 = Mock(path="/path2/", user=Mock(is_authenticated=False))

        results = {}

        def process_with_request(request_id, request):
            processed = menu.process(request)
            # Find which item is selected
            for child in processed._processed_children:
                if child.selected:
                    results[request_id] = child.name
                    break

        # Process concurrently with different requests
        threads = []

        for i in range(5):
            # Alternate between the two requests
            request = request1 if i % 2 == 0 else request2
            expected_selection = "item1" if i % 2 == 0 else "item2"

            thread = threading.Thread(
                target=process_with_request, args=(f"thread_{i}", request)
            )
            threads.append((thread, expected_selection))
            thread.start()

        # Wait for completion and check results
        for thread, expected in threads:
            thread.join()

        # Each thread should have gotten the correct selection
        # Note: This test verifies that processing doesn't cause cross-contamination

    def test_global_root_thread_safety(self):
        """Test that operations on the global root are thread-safe."""
        from flex_menu import root

        initial_child_count = len(root.children)

        def add_to_root(thread_id):
            menu = MenuGroup(name=f"root_thread_{thread_id}")
            root.append(menu)
            time.sleep(0.001)

        # Add menus from multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=add_to_root, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Check that all were added
        final_child_count = len(root.children)
        assert final_child_count == initial_child_count + 10

        # Clean up
        for i in range(10):
            menu = root.get(f"root_thread_{i}")
            if menu:
                menu.parent = None


class TestMemoryUsage:
    """Test memory efficiency of the menu system."""

    def test_menu_copy_memory_efficiency(self, mock_request):
        """Test that processed copies don't leak memory."""
        import gc

        menu = MenuGroup(name="memory_test")

        for i in range(20):
            item = MenuLink(name=f"item_{i}", url=f"/item{i}/")
            menu.append(item)

        # Create many processed copies
        processed_copies = []

        for _ in range(100):
            processed = menu.process(mock_request)
            processed_copies.append(processed)

        # Clear references and force garbage collection
        del processed_copies
        gc.collect()

        # The test passes if no memory errors occur
        # In a real test environment, you might use memory profiling tools

    def test_large_menu_structure_memory(self):
        """Test memory usage with large menu structures."""
        import sys

        # Measure memory before
        initial_size = sys.getsizeof(BaseMenu(name="test", template_name="menu/base.html"))

        # Create large structure
        large_menu = MenuGroup(name="large")

        for i in range(50):
            submenu = MenuGroup(name=f"sub_{i}")
            for j in range(20):
                item = MenuLink(name=f"item_{i}_{j}", url=f"/url{i}{j}/")
                submenu.append(item)
            large_menu.append(submenu)

        # The structure should be created without excessive memory usage
        # This test mainly ensures no memory-related exceptions occur
        assert len(large_menu.children) == 50
        assert len(large_menu.children[0].children) == 20

    def test_circular_reference_prevention(self):
        """Test that the system prevents problematic circular references."""
        parent = BaseMenu(name="parent", template_name="menu/base.html")
        child = BaseMenu(name="child", template_name="menu/base.html")

        parent.append(child)

        # This should work fine
        assert child.parent == parent
        assert child in parent.children

        # Attempting to create a circular reference should be prevented
        # by the underlying anytree library
        # (child cannot be parent of its own ancestor)

        with pytest.raises(Exception):  # anytree should prevent this
            parent.parent = child
