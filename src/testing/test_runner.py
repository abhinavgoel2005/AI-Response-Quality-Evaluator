"""
End-to-End Test Runner

Development of AI Response Validation System
with Hallucination Detection Assistance

Executes the complete End-to-End Testing suite and
stores the results in JSON format.
"""

import json
import os
import time
from datetime import datetime

from testing.test_cases import get_test_suite


class TestRunner:

    def __init__(self):

        self.results = []

        self.total_tests = 0

        self.passed = 0

        self.failed = 0

        self.start_time = datetime.now()

    # ==================================================
    # Run Single Test
    # ==================================================

    def run_test(

        self,

        test_name,

        test_function

    ):

        print()

        print("=" * 70)

        print(f"Running Test : {test_name}")

        print("=" * 70)

        start = time.perf_counter()

        try:

            result = test_function()

            execution_time = round(

                time.perf_counter() - start,

                3

            )

            if result is None:

                result = {}

            status = result.get(

                "status",

                "PASS"

            )

            if status.upper() == "PASS":

                self.passed += 1

            else:

                self.failed += 1

            self.results.append(

                {

                    "test_name": test_name,

                    "status": status,

                    "execution_time": execution_time,

                    "details": result

                }

            )

            print(f"Status : {status}")

            print(f"Time   : {execution_time} sec")

        except Exception as error:

            execution_time = round(

                time.perf_counter() - start,

                3

            )

            self.failed += 1

            self.results.append(

                {

                    "test_name": test_name,

                    "status": "FAIL",

                    "execution_time": execution_time,

                    "error": str(error)

                }

            )

            print("Status : FAIL")

            print(f"Error  : {error}")

        self.total_tests += 1

    # ==================================================
    # Execute Entire Suite
    # ==================================================

    def execute(

        self,

        test_suite

    ):

        print()

        print("#" * 70)

        print("END-TO-END TESTING")

        print("Development of AI Response Validation System")

        print("#" * 70)

        for name, function in test_suite:

            self.run_test(

                name,

                function

            )

        self.save_results()

        self.print_summary()

    # ==================================================
    # Save JSON
    # ==================================================

    def save_results(self):

        output_path = os.path.join(

            os.path.dirname(__file__),

            "test_results.json"

        )

        with open(

            output_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                self.results,

                file,

                indent=4

            )

        print()

        print("Test results saved to:")

        print(output_path)

    # ==================================================
    # Print Summary
    # ==================================================

    def print_summary(self):

        duration = (

            datetime.now()

            - self.start_time

        ).total_seconds()

        print()

        print("=" * 70)

        print("TEST SUMMARY")

        print("=" * 70)

        print(f"Total Tests : {self.total_tests}")

        print(f"Passed      : {self.passed}")

        print(f"Failed      : {self.failed}")

        print(f"Duration    : {round(duration,2)} sec")

        print("=" * 70)

        if self.failed == 0:

            print()

            print("All End-to-End tests completed successfully.")

        else:

            print()

            print("Some tests failed. Please review test_results.json.")


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    runner = TestRunner()

    runner.execute(

        get_test_suite()

    )