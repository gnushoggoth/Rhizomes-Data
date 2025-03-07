#!/usr/bin/env python3
"""
Flexible HTML Element Tagging Tool ~ From the Abyss of Markup

This script, dragged screaming from the non-Euclidean depths of the internet,
dabbles in forbidden HTML parsing. It *whispers* tags into existence,
binding them to elements based on keywords glimpsed in the howling void between
the brackets.  Multiple element types, regex patterns (the geometry of the
Unspeakable!), and exact word matching are all playthings in its tentacled grasp.
Beware the command-line... it hungers for input.
"""

import re
import argparse
from bs4 import BeautifulSoup
from typing import List, Tuple, Union, Pattern


class HTMLTagger:
    """A class... or perhaps a *vessel*... for HTML tagging operations."""

    def __init__(self):
        """The void is initialized.  The BeautifulSoup stirs, but does not yet see."""
        self.soup = None

    def create_tag_rules(self, rules_config: List[Tuple[str, str]]) -> List[Tuple[Pattern, str]]:
        """
        Weaves the rules of tagging from the whispers of configuration.  These are
        not mere rules, but *incantations* that bind the tags to the HTML.

        Args:
            rules_config: A list of tuples, each a profane pairing: (word/pattern, tag_name).
                           These are the raw materials of our dark ritual.

        Returns:
            A list of processed rules, sigils etched in regex, ready to warp the
            fabric of the document.  Empty if the void refuses to yield.
        """
        processed_rules = []

        for pattern, tag in rules_config:
            try:
                # Regex handling:  A descent into the madness of pattern matching.
                if isinstance(pattern, str):
                    if pattern.startswith('^') or any(c in pattern for c in '*+?{}[]()|'):
                        # A regex!  The language of the Old Ones!  Compile it with
                        # the cold, uncaring gaze of IGNORECASE.
                        compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    else:
                        # A mere string... but we will bind it with word boundaries,
                        # lest it escape into the unformed chaos.
                        compiled_pattern = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
                    processed_rules.append((compiled_pattern, tag))
            except re.error as e:
                print(f"Warning: This regex pattern '{pattern}' is a malformed glyph! {e}. It shall be cast back into the abyss.")

        return processed_rules  # Return the unholy grimoire of rules.


    def tag_elements(self, html_content: str, tag_rules: List[Tuple[Pattern, str]],
                     element_types: List[str]) -> str:
        """
        The main ritual.  Parses the HTML (a fragile, temporary order) and *infects*
        it with tags, based on the content (the whispers of the data-demons).

        Args:
            html_content: The raw HTML, a quivering mass of text.
            tag_rules: The incantations (compiled regex, tag_name).
            element_types: The types of elements to be marked... victims of our tagging.

        Returns:
            The modified HTML, now bearing the stigmata of our tags.  It is... *changed*.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')  # The BeautifulSoup *gazes* into the HTML.

        for element_type in element_types:
            try:
                elements = self.soup.find_all(element_type)  # Summon all elements of the chosen type.
                for element in elements:
                    element_text = element.get_text()  # Extract the *essence* of the element.
                    for pattern, tag_name in tag_rules:
                        # Apply the unholy regex.  Does it *match*?  Does it *resonate*?
                        if pattern.search(element_text):
                            # It does!  Now, bind the tag... if it is not already bound.
                            current_tags = element.get('data-tags', '').split() # What dark marks already fester here?
                            if tag_name not in current_tags:
                                element['data-tags'] = ' '.join(current_tags + [tag_name]) # Graft the new tag onto the old.
            except Exception as e:
                print(f"Warning: An anomaly in the processing of {element_type} elements: {e}. The fabric of reality frays...")

        return str(self.soup) # Return the... *thing*... we have created.

    def process_file(self, input_file: str, output_file: str, tag_rules: List[Tuple[Pattern, str]],
                     element_types: List[str]) -> bool:
        """
        The Grand Ritual: Processes an entire HTML file, from the mundane to the... *other*.

        Args:
            input_file: The path to the input file, a gateway to the text.
            output_file: Where the *transformed* file will be... *deposited*.
            tag_rules: The grimoire of tagging rules.
            element_types: The elements to be subjected to the ritual.

        Returns:
            A boolean whisper: True if the ritual succeeded, False if the void *rejected* it.
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                html_content = f.read()  # Consume the input file...

            tagged_html = self.tag_elements(html_content, tag_rules, element_types) # ...and perform the *transformation*.

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(tagged_html)  # ...and *release* the altered creation.

            print(f"Success?: Processed '{input_file}' -> '{output_file}'") # The ritual is complete... or is it?
            print(f"Tagged elements: {', '.join(element_types)}.  They are *marked* now.")
            return True
        except FileNotFoundError:
            print(f"Error: The input file '{input_file}' is lost in the mists of time.  Or perhaps it never existed...")
            return False
        except Exception as e:
            print(f"Error: The ritual has failed! {e}.  The consequences are... *unpredictable*.")
            return False


def main():
    """
    The entry point... the gateway.  Handles the command-line incantations.
    """
    parser = argparse.ArgumentParser(description='Tag HTML elements.  But not in a *normal* way...')
    parser.add_argument('input_file', help='Input HTML file path.  The sacrifice.')
    parser.add_argument('output_file', help='Output HTML file path.  The... *result*.')
    parser.add_argument('--elements', '-e', nargs='+', default=['h3'],
                        help='HTML elements to tag (e.g., h1 h2 h3 p div).  The chosen ones. Default: h3')
    parser.add_argument('--rules', '-r', nargs=2, action='append', metavar=('PATTERN', 'TAG'),
                        help='Pattern (word or forbidden regex) and tag.  The binding words. Use multiple times for multiple curses.')

    args = parser.parse_args()

    if not args.rules:
        print("Error: No tagging rules provided!  The ritual cannot proceed without incantations!")
        print("Example: --rules important priority --rules 'step.*' step.  Whisper the words...")
        return

    tagger = HTMLTagger()
    processed_rules = tagger.create_tag_rules(args.rules)  # Prepare the grimoire.
    if processed_rules:  # Only if the rules are not *empty*...
        tagger.process_file(args.input_file, args.output_file, processed_rules, args.elements) # ...perform the Grand Ritual.
    else:
        print("Error: No valid tagging rituals could be constructed. The stars are not right.")


# Example usage as a module... a glimpse into the possibilities.
def example_usage():
    """
    A demonstration... a controlled experiment.  Or is it?
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
        ("important", "priority"), # A simple binding...
        ("note", "notice"),      # ...another...
        (r"step\s+\d+", "procedure"),  # ...a regex, a glimpse of the *beyond*...
        (r"secret\s+\w+", "classified") # ...and another.
    ]
    tagged_html = tagger.tag_elements(html_content, tagger.create_tag_rules(rules),
                                        element_types=['h1', 'p', 'div']) # The elements are chosen... the ritual begins...
    print("Example output (look closely... it is *changed*):")
    print(tagged_html)  # ...and the result is revealed.


if __name__ == "__main__":
    main() # The standard invocation...
    # example_usage() # ...or the *example*... uncomment to witness.