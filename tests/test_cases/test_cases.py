"""Test cases for the Highrise FAQ Chatbot"""

from typing import Dict, List, Any

TEST_CASES: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "Basic Functionality": {
        "Greetings": [
            {"input": "hello", "expected_contains": ["hello", "help", "today"]},
            {"input": "hi there!", "expected_contains": ["hello", "help"]},
            {"input": "good morning", "expected_contains": ["hello", "help"]}
        ],
        "Farewells": [
            {"input": "goodbye", "expected_contains": ["goodbye", "come back"]},
            {"input": "thanks", "expected_contains": ["goodbye", "questions"]}
        ],
        "Empty/Short Questions": [
            {"input": "", "expected_contains": ["complete question"]},
            {"input": "ok", "expected_contains": ["complete question"]}
        ]
    },
    "Synonym Handling": {
        "Currency Terms": [
            {"input": "How do I get coins?", "expected_contains": ["gold"]},
            {"input": "What are credits used for?", "expected_contains": ["gold"]},
            {"input": "How to earn money?", "expected_contains": ["gold"]}
        ],
        "Avatar Terms": [
            {"input": "How to change my character?", "expected_contains": ["avatar"]},
            {"input": "Customize profile", "expected_contains": ["avatar", "customize"]}
        ]
    },
    "Typo Handling": {
        "Common Misspellings": [
            {"input": "How do I custmize my avtar?", "expected_contains": ["avatar", "customize"]},
            {"input": "Where can I buy gld?", "expected_contains": ["gold"]},
            {"input": "How to reportt someone?", "expected_contains": ["report"]}
        ]
    },
    "Multi-part Questions": {
        "Complex Queries": [
            {
                "input": "How do I create an account and customize my avatar?",
                "expected_contains": ["account", "create", "avatar", "customize"]
            },
            {
                "input": "What are gold bars and how do I use them?",
                "expected_contains": ["gold", "bars", "use"]
            }
        ]
    },
    "Context Handling": {
        "Vague Questions": [
            {
                "input": "How much does it cost?",
                "expected_contains": ["specify", "what", "asking about"]
            },
            {
                "input": "When will it be available?",
                "expected_contains": ["which", "feature", "specify"]
            }
        ]
    },
    "Edge Cases": {
        "Special Characters": [
            {"input": "How do I report ???", "expected_contains": ["report"]},
            {"input": "!@#$%^&*()", "expected_contains": ["complete question"]}
        ],
        "Long Questions": [
            {
                "input": "I want to know everything about the game and how to play it and what features it has and how to make friends and customize my avatar and earn gold and participate in events?",
                "expected_contains": ["specific", "one question"]
            }
        ]
    }
} 