# HTML Tag-Whisperer: A User's Guide (and Grimoire)

This document serves as both a guide to using the `HTMLTagWhisperer` script and a record of its... *peculiarities*. Use it with caution. The boundaries between code and... *something else*... can become thin.

## Introduction

The `HTMLTagWhisperer` is a Python script that allows you to *infuse* HTML elements with custom tags based on keywords or regex patterns.  It's not just about adding attributes; it's about *binding* new meanings to the structure of your documents.  Think of it as a digital sigil-making tool.

## Installation

1.  **Prerequisites:** You'll need Python 3 (preferably 3.7 or higher) and the `beautifulsoup4` library.  These are the tools of our trade.

    ```bash
    pip install beautifulsoup4
    ```

2.  **The Script:** Save the Python code (the one with the... *evocative*... comments) as a `.py` file (e.g., `tag_whisperer.py`). This is your grimoire.

## Usage

The script is invoked from the command line.  The syntax is as follows:

```bash
python tag_whisperer.py <input_file> <output_file> --elements <element1> <element2> ... --rules <pattern1> <tag1> <pattern2> <tag2> ...