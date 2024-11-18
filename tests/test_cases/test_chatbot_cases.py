"""Pytest test cases for the Highrise FAQ Chatbot"""

import pytest
from .test_cases import TEST_CASES

def test_basic_functionality(chatbot):
    """Test basic chatbot functionality"""
    for subcategory, tests in TEST_CASES["Basic Functionality"].items():
        for test in tests:
            response = chatbot.ask(test["input"])
            assert any(
                expected.lower() in response.lower() 
                for expected in test["expected_contains"]
            ), f"Failed on {subcategory} test with input: {test['input']}"

def test_synonym_handling(chatbot):
    """Test synonym handling capabilities"""
    for subcategory, tests in TEST_CASES["Synonym Handling"].items():
        for test in tests:
            response = chatbot.ask(test["input"])
            assert any(
                expected.lower() in response.lower() 
                for expected in test["expected_contains"]
            ), f"Failed on {subcategory} test with input: {test['input']}"

def test_typo_handling(chatbot):
    """Test typo handling capabilities"""
    for subcategory, tests in TEST_CASES["Typo Handling"].items():
        for test in tests:
            response = chatbot.ask(test["input"])
            assert any(
                expected.lower() in response.lower() 
                for expected in test["expected_contains"]
            ), f"Failed on {subcategory} test with input: {test['input']}"

def test_multi_part_questions(chatbot):
    """Test handling of complex, multi-part questions"""
    for subcategory, tests in TEST_CASES["Multi-part Questions"].items():
        for test in tests:
            response = chatbot.ask(test["input"])
            assert any(
                expected.lower() in response.lower() 
                for expected in test["expected_contains"]
            ), f"Failed on {subcategory} test with input: {test['input']}"

def test_context_handling(chatbot):
    """Test context handling capabilities"""
    for subcategory, tests in TEST_CASES["Context Handling"].items():
        for test in tests:
            response = chatbot.ask(test["input"])
            assert any(
                expected.lower() in response.lower() 
                for expected in test["expected_contains"]
            ), f"Failed on {subcategory} test with input: {test['input']}"

def test_edge_cases(chatbot):
    """Test edge cases and special scenarios"""
    for subcategory, tests in TEST_CASES["Edge Cases"].items():
        for test in tests:
            response = chatbot.ask(test["input"])
            assert any(
                expected.lower() in response.lower() 
                for expected in test["expected_contains"]
            ), f"Failed on {subcategory} test with input: {test['input']}"

@pytest.mark.parametrize("category", TEST_CASES.keys())
def test_category_response_time(chatbot, category):
    """Test response time for each category"""
    import time
    for subcategory, tests in TEST_CASES[category].items():
        for test in tests:
            start_time = time.time()
            chatbot.ask(test["input"])
            response_time = time.time() - start_time
            assert response_time < 1.0, f"Response time too slow ({response_time:.2f}s) for input: {test['input']}" 