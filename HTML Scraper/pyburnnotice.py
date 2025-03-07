#!/usr/bin/env python3
"""
Flexible HTML Element Tagging Tool

This script parses HTML content and adds specified tags to HTML elements
that contain certain keywords. Supports multiple element types, regex patterns,
and exact word matching with command-line input flexibility.
"""

import re
import argparse
from bs4 import BeautifulSoup
from typing import List, Tuple, Union, Pattern


class HTMLTagger:
    """Class to handle HTML tagging operations"""

    def __init__(self):
        self.soup = None

    def create_tag_rules(self, rules_config: List[Tuple[str, str]]) -> List[Tuple[Union[Pattern, str], str]]:
        """
        Process tag rules from configuration
        
        Args:
            rules_config: List of tuples (word/pattern, tag_name)
        
        Returns:
            Processed rules list with compiled regex patterns
        """
        processed_rules = []
        
        for pattern, tag in rules_config:
            try:
                # If it looks like a regex pattern (starts with ^ or contains special chars)
                if isinstance(pattern, str) and (pattern.startswith('^') or '*' in pattern or '+' in pattern):
                    pattern = re.compile(pattern, re.IGNORECASE)
                elif isinstance(pattern, str):
                    # Convert to word boundary regex for exact word matching
                    pattern = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
                processed_rules.append((pattern, tag))
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}. Skipping this rule.")
        
        return processed_rules

    def tag_elements(self, html_content: str, tag_rules: List[Tuple[Union[Pattern, str], str]], 
                    element_types: List[str]) -> str:
        """
        Parse HTML and add tags to specified elements based on content
        
        Args:
            html_content: HTML content as string
            tag_rules: List of tuples (word/pattern, tag_name)
            element_types: List of HTML element types to target
        
        Returns:
            Modified HTML content
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')
        
        for element_type in element_types:
            try:
                elements = self.soup.find_all(element_type)
                for element in elements:
                    element_text = element.get_text()
                    for pattern, tag_name in tag_rules:
                        match = (pattern.search(element_text) if isinstance(pattern, Pattern) 
                                else pattern.lower() in element_text.lower())
                        if match:
                            current_tags = element.get('data-tags', '').split()
                            if tag_name not in current_tags:
                                element['data-tags'] = ' '.join(current_tags + [tag_name])
            except Exception as e:
                print(f"Warning: Error processing {element_type} elements: {e}")
        
        return str(self.soup)

    def process_file(self, input_file: str, output_file: str, tag_rules: List[Tuple[Union[Pattern, str], str]], 
                    element_types: List[str]) -> bool:
        """
        Process an HTML file and save the tagged output
        
        Returns:
            Boolean indicating success
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
        except Exception as e:
            print(f"Error: Failed to process file: {e}")
            return False


def main():
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
    if processed_rules:
        tagger.process_file(args.input_file, args.output_file, processed_rules, args.elements)


# Example usage as a module
def example_usage():
    tagger = HTMLTagger()
    html_content = """
    <html>
        <h1>Important Title</h1>
        <p>This is a note for users</p>
        <div>Step 1: Begin here</div>
    </html>
    """
    rules = [
        ("important", "priority"),
        ("note", "notice"),
        (r"step\s+\d+", "procedure")
    ]
    tagged_html = tagger.tag_elements(html_content, tagger.create_tag_rules(rules), 
                                    element_types=['h1', 'p', 'div'])
    print("Example output:")
    print(tagged_html)


if __name__ == "__main__":
    main()
    # Uncomment to test example
    # example_usage()