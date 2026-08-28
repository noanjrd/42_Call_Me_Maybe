import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument(
        "--functions_definition",
        type=str,
        nargs="?", 
        required=False,
        default="src/data/input/functions_definition.json",
        help=""
        )

    parser.add_argument(
        "--input",
        type=str,
        nargs="?", 
        required=False,
        default="src/data/input/function_calling_tests.json",
        help=""
        )

    parser.add_argument(
        "--output",
        type=str,
        nargs="?", 
        required=False,
        default="src/data/output/function_calling_results.json",
        help=""
        )

    return parser.parse_args()