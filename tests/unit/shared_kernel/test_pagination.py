import pytest

from camp_match.shared_kernel.application.pagination import Page, PageRequest


def test_page_request_valid_defaults():
    req = PageRequest()
    assert req.page == 1
    assert req.page_size == 20


def test_page_request_custom_valid():
    req = PageRequest(page=2, page_size=50)
    assert req.page == 2
    assert req.page_size == 50


def test_page_request_invalid_page():
    with pytest.raises(ValueError, match="page must be >= 1"):
        PageRequest(page=0)


def test_page_request_invalid_page_size_low():
    with pytest.raises(ValueError, match="page_size must be between 1 and 100"):
        PageRequest(page_size=0)


def test_page_request_invalid_page_size_high():
    with pytest.raises(ValueError, match="page_size must be between 1 and 100"):
        PageRequest(page_size=101)


def test_page_data_structure():
    items = ["a", "b", "c"]
    page = Page(items=items, total=10, page=1, page_size=3)

    assert page.items == items
    assert page.total == 10
    assert page.page == 1
    assert page.page_size == 3
