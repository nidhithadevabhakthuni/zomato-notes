from typing import List, Dict, Any, Optional

def insertion_sort_by_key(items: List[Dict], key: str) -> List[Dict]:
    """
    Sorts list of dictionaries in descending order by a numeric key
    using insertion sort algorithm from scratch.
    """
    if not items:
        return items
    
    # Create a copy to avoid modifying the original
    sorted_items = items.copy()
    
    for i in range(1, len(sorted_items)):
        current = sorted_items[i]
        j = i - 1
        
        # Move elements that are less than current one position ahead
        while j >= 0 and sorted_items[j].get(key, 0) < current.get(key, 0):
            sorted_items[j + 1] = sorted_items[j]
            j -= 1
        sorted_items[j + 1] = current
    
    return sorted_items

def binary_search_iterative(sorted_titles: List[str], target: str) -> int:
    """
    Iterative binary search for target in sorted list.
    Returns index or -1 if not found.
    """
    start = 0
    end = len(sorted_titles) - 1
    
    while start <= end:
        mid = start + (end - start) // 2
        if sorted_titles[mid] == target:
            return mid
        elif sorted_titles[mid] < target:
            start = mid + 1
        else:
            end = mid - 1
    
    return -1

def binary_search_recursive(sorted_titles: List[str], target: str, start: int, end: int) -> int:
    """
    Recursive binary search for target in sorted list.
    Returns index or -1 if not found.
    """
    if start > end:
        return -1
    
    mid = start + (end - start) // 2
    
    if sorted_titles[mid] == target:
        return mid
    elif sorted_titles[mid] < target:
        return binary_search_recursive(sorted_titles, target, mid + 1, end)
    else:
        return binary_search_recursive(sorted_titles, target, start, mid - 1)

def linear_search(items: List[Dict], key: str, value: Any) -> Optional[Dict]:
    """
    Linear search using found-flag pattern.
    Returns first matching dict or None.
    """
    found = False
    result = None
    
    for item in items:
        if item.get(key) == value:
            found = True
            result = item
            break
    
    return result