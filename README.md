# Cypris Patent XML Parser

**Kevin Singh**

A Python cli tool used to clean malformed XML + extracts attributes from the cleaned patent XML. 


## Overview

This project solves the challenge of extracting `doc-number` values from patent XML documents stored in Google Cloud Storage. The tool handles:
- Malformed XML (missing closing tags, incomplete attributes, missing `>` brackets)
- Priority-based extraction (e.g., EPO format first, then patent-office)
- Flexible attribute extraction with custom XPath queries

## Features

- **XML Parsing**: Automatically fixes common XML malformations
  - Missing closing `>` brackets
  - Attributes without values (e.g., `us-series-code` becomes `us-series-code=""`)
  - Placeholder `...` removal
- **Priority Ordering**: Extract attributes in a specified priority order
- **CLI Support**: Command-line interface for easy integration
- **Comprehensive Tests**: Includes some unit tests to verify functionality

## Project Structure

```
.
├── cypris_xml_parser.py           # Core XML cleaning/parsing logic
├── patent_attribute_extraction.py # Main extraction class with CLI
├── input_xmls/
│   └── test_case_1.txt            # Sample malformed XML file
├── tests/
│   ├── __init__.py
│   └── test_patent_attribute_extraction.py  # Unit tests
├── requirements.txt                # Python dependencies
├── setup.sh                        # Automated setup script
└── README.md                       # This file
```

## Installation

```bash
# Create virtual environment
uv venv

# Activate virtual environment (Mac)
source .venv/bin/activate
# Activate virtual environment (Windows)
.venv\Scripts\activate.bat

# Install dependencies
uv pip install -r requirements.txt
```

## Usage

**Coding challenge solution**: 
Run this one for the Cypris coding challenge assessment solution!
```bash
python run_assesment_scenario.py
```

Other ways to use the tool are below.


### Command Line Interface

**Basic usage** (extract doc-numbers with default settings):
```bash
python patent_attribute_extraction.py input_xmls/test_case_1.txt
```

**Extract multiple attributes**:
```bash
python patent_attribute_extraction.py input_xmls/test_case_1.txt --attributes doc-number country lang
```

**Custom XPath**:
```bash
python patent_attribute_extraction.py input_xmls/test_case_1.txt --xpath './/document-id[@format="epo"]'
```

**Help**:
```bash
python patent_attribute_extraction.py --help
```


### Python Code Example

If you want to use custom priority ordering!

```python
from patent_attribute_extraction import PatentAttributeExtractor, DEFAULT_PRIORITY_ORDER

# Read XML file
with open('input_xmls/test_case_1.txt', 'r') as f:
    xml_data = f.read()

# Create extractor
extractor = PatentAttributeExtractor(xml_data)

# Extract doc-numbers with default priority (EPO first, then patent-office)
doc_numbers = extractor.extract_attributes(priority_ordering=DEFAULT_PRIORITY_ORDER)
print(doc_numbers)
# Output: ['999000888', '66667777']

# Extract multiple attributes (returns DataFrame)
result = extractor.extract_attributes(
    attributes=['doc-number', 'country', 'lang'],
    priority_ordering=DEFAULT_PRIORITY_ORDER
)
print(result)

# Custom priority order
custom_priority = {
    1: {
        'attribute': "load-source",
        "values": ["patent-office"]
    },
    2: {
        'attribute': "format",
        "values": ["epo"]
    }
}

doc_numbers = extractor.extract_attributes(priority_ordering=custom_priority)
print(doc_numbers)
# Output: ['66667777', '999000888']  # patent-office first now
```

## Assumptions

The following assumptions are made about the XML structure:

1. **XML may be malformed**: Missing closing tags, incomplete tags, missing `>`
2. **Attributes without values**: Set to blank `""` (e.g., `us-series-code`)
3. **document-id elements**: Have a `format` attribute that determines priority
4. **Priority order**: `epo` format first, then `patent-office`, then `original`, then `docdb`
5. **doc-number elements**: Nested within `document-id` elements
6. **Multiple document-id elements**: May exist within `application-reference`
7. **Placeholder data**: XML may contain `...` representing omitted data (removed during parsing)
8. **Implicit closing**: If a new opening tag is encountered without a closing tag for the previous element, the previous element is assumed to be implicitly closed

## Testing

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_patent_attribute_extraction -v

# Run with pytest (if installed)
pytest tests/ -v
```

## Example Output

Given the sample XML in `input_xmls/test_case_1.txt`:

```bash
$ python patent_attribute_extraction.py input_xmls/test_case_1.txt
```

Output:
```
Extracted attributes (in priority order):
==================================================
1. 999000888
2. 66667777
==================================================
Total: 2 values extracted
```

The output shows that `999000888` (EPO format) comes before `66667777` (patent-office format) based on the default priority ordering.
