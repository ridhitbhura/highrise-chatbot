"""Test runner for the Highrise FAQ Chatbot"""

import os
import json
import logging
from datetime import datetime
from typing import Dict
from src.main.simple_faq_chatbot import SimpleFAQChatbot
from .test_cases.test_cases import TEST_CASES

class ChatbotTester:
    def __init__(self):
        # Define base directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logs_dir = os.path.join(self.base_dir, 'logs', 'tests')
        self.results_dir = os.path.join(self.base_dir, 'tests', 'results')
        
        # Create necessary directories
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize chatbot
        self.chatbot = SimpleFAQChatbot('data/highrise_faq.json')
        
    def _setup_logging(self):
        """Configure test logging"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.logs_dir, f'test_log_{timestamp}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def run_tests(self) -> Dict:
        """Run all test cases and return results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {
            "timestamp": timestamp,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "results_by_category": {}
        }

        for category, subcategories in TEST_CASES.items():
            results["results_by_category"][category] = {
                "passed": 0,
                "failed": 0,
                "details": []
            }

            for subcategory, tests in subcategories.items():
                logging.info(f"Testing {category} - {subcategory}")
                
                for test in tests:
                    results["total_tests"] += 1
                    try:
                        response = self.chatbot.ask(test["input"])
                        contains_expected = any(
                            expected.lower() in response.lower() 
                            for expected in test["expected_contains"]
                        )
                        
                        if contains_expected:
                            results["passed"] += 1
                            results["results_by_category"][category]["passed"] += 1
                        else:
                            results["failed"] += 1
                            results["results_by_category"][category]["failed"] += 1
                            
                        results["results_by_category"][category]["details"].append({
                            "subcategory": subcategory,
                            "input": test["input"],
                            "response": response,
                            "expected_contains": test["expected_contains"],
                            "status": "PASS" if contains_expected else "FAIL"
                        })
                        
                    except Exception as e:
                        logging.error(f"Error testing {test['input']}: {str(e)}")
                        results["failed"] += 1
                        results["results_by_category"][category]["failed"] += 1
                        results["results_by_category"][category]["details"].append({
                            "subcategory": subcategory,
                            "input": test["input"],
                            "error": str(e),
                            "status": "ERROR"
                        })

        # Save results
        results_file = os.path.join(self.results_dir, f'test_results_{timestamp}.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate test report"""
        timestamp = results["timestamp"]
        summary = f"""Highrise FAQ Chatbot Test Summary
================================

Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Tests: {results['total_tests']}
Passed: {results['passed']}
Failed: {results['failed']}
Success Rate: {(results['passed']/results['total_tests'])*100:.2f}%

Category Summary:
"""
        
        for category, data in results["results_by_category"].items():
            summary += f"\n{category}:"
            summary += f"\n  Passed: {data['passed']}"
            summary += f"\n  Failed: {data['failed']}"
            
            # Add failed test details
            failed_tests = [t for t in data['details'] if t['status'] != 'PASS']
            if failed_tests:
                summary += "\n  Failed Tests:"
                for test in failed_tests:
                    summary += f"\n    - Input: {test['input']}"
                    if 'error' in test:
                        summary += f"\n      Error: {test['error']}"
                    else:
                        summary += f"\n      Expected: {test['expected_contains']}"
                        summary += f"\n      Got: {test['response']}"
        
        # Save summary
        summary_file = os.path.join(self.results_dir, f'test_summary_{timestamp}.txt')
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return summary

def main():
    tester = ChatbotTester()
    print("Starting chatbot tests...")
    
    results = tester.run_tests()
    summary = tester.generate_report(results)
    
    print("\nTest Summary:")
    print(summary)

if __name__ == "__main__":
    main() 