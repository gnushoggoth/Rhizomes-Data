#!/usr/bin/env python3
"""
Flexible HTML Element Tagging Tool

This script parses HTML content and adds specified tags to HTML elements
that contain certain keywords. Supports multiple element types, regex patterns,
and exact word matching with command-line input flexibility.  It also includes
error handling and more robust regex processing.
"""

import re
import argparse
from bs4 import BeautifulSoup
from typing import List, Tuple, Union, Pattern


class HTMLTagger:
    """Class to handle HTML tagging operations"""

    def __init__(self):
        self.soup = None

    def create_tag_rules(self, rules_config: List[Tuple[str, str]]) -> List[Tuple[Pattern, str]]:
        """
        Process tag rules from configuration, compiling them into regex patterns.

        Args:
            rules_config: List of tuples (word/pattern, tag_name)

        Returns:
            Processed rules list with compiled regex patterns.  Returns an empty
            list if no valid rules are found. Invalid regexes are skipped with
            a warning.
        """
        processed_rules = []

        for pattern, tag in rules_config:
            try:
                # More robust regex handling:
                if isinstance(pattern, str):
                    if pattern.startswith('^') or any(c in pattern for c in '*+?{}[]()|'):
                        # It's likely a regex.  Compile with IGNORECASE.
                        compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    else:
                        # Treat as a literal string, but match whole words only.
                        compiled_pattern = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
                    processed_rules.append((compiled_pattern, tag))
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}. Skipping this rule.")

        return processed_rules


    def tag_elements(self, html_content: str, tag_rules: List[Tuple[Pattern, str]],
                     element_types: List[str]) -> str:
        """
        Parse HTML and add tags to specified elements based on content.

        Args:
            html_content: HTML content as string.
            tag_rules: List of tuples (compiled regex pattern, tag_name).
            element_types: List of HTML element types to target.

        Returns:
            Modified HTML content.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')

        for element_type in element_types:
            try:
                elements = self.soup.find_all(element_type)  # Find all elements of the specified type
                for element in elements:
                    element_text = element.get_text()
                    for pattern, tag_name in tag_rules:
                        #  Use the compiled regex pattern for matching.
                        if pattern.search(element_text):
                            # Get existing tags, handling cases where the attribute is missing.
                            current_tags = element.get('data-tags', '').split()
                            if tag_name not in current_tags:
                                element['data-tags'] = ' '.join(current_tags + [tag_name])
            except Exception as e:
                print(f"Warning: Error processing {element_type} elements: {e}")

        return str(self.soup)

    def process_file(self, input_file: str, output_file: str, tag_rules: List[Tuple[Pattern, str]],
                     element_types: List[str]) -> bool:
        """
        Process an HTML file, tag it, and save the tagged output.

        Args:
            input_file: Path to the input HTML file.
            output_file: Path to the output HTML file.
            tag_rules: List of tuples (compiled regex pattern, tag_name).
            element_types: List of HTML element types to target.

        Returns:
            Boolean indicating success.
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            tagged_html = self.tag_elements(html_content, tag_rules, element_types)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(tagged_html)

            print(f"Success: Processed '{input_file}' -> '{output_file}'")
            print(f"Tagged elements: {', '.join(element_types)}")
            return True
        except FileNotFoundError:
            print(f"Error: Input file not found: {input_file}")
            return False
        except Exception as e:
            print(f"Error: Failed to process file: {e}")
            return False


def main():
    """
    Main function to handle command-line arguments and processing.
    """
    parser = argparse.ArgumentParser(description='Tag HTML elements based on their content')
    parser.add_argument('input_file', help='Input HTML file path')
    parser.add_argument('output_file', help='Output HTML file path')
    parser.add_argument('--elements', '-e', nargs='+', default=['h3'],
                        help='HTML elements to tag (e.g., h1 h2 h3 p div). Default: h3')
    parser.add_argument('--rules', '-r', nargs=2, action='append', metavar=('PATTERN', 'TAG'),
                        help='Pattern (word or regex) and tag to apply. Use multiple times for multiple rules.')

    args = parser.parse_args()

    if not args.rules:
        print("Error: No tagging rules specified. Use --rules to define at least one rule.")
        print("Example: --rules important priority --rules 'step.*' step")
        return

    tagger = HTMLTagger()
    processed_rules = tagger.create_tag_rules(args.rules)
    if processed_rules:  # Only proceed if we have valid rules
        tagger.process_file(args.input_file, args.output_file, processed_rules, args.elements)
    else:
        print("Error: No valid tagging rules were created.")


# Example usage as a module
def example_usage():
    """
    Demonstrates how to use the HTMLTagger class as a module.
    """
    tagger = HTMLTagger()
    html_content = """
    <html>
        <h1>Important Title</h1>
        <p>This is a note for users</p>
        <div>Step 1: Begin here</div>
        <p>Another important note.</p>
        <div>Step 2: Continue...</div>
        <div class="hidden">secret step</div>
    </html>
    """
    rules = [
        ("important", "priority"),
        ("note", "notice"),
        (r"step\s+\d+", "procedure"),  # Corrected regex
        (r"secret\s+\w+", "classified") # Added a new rule for demonstration
    ]
    tagged_html = tagger.tag_elements(html_content, tagger.create_tag_rules(rules),
                                        element_types=['h1', 'p', 'div'])
    print("Example output:")
    print(tagged_html)


if __name__ == "__main__":
    main()
    # example_usage() # Uncomment to run the example