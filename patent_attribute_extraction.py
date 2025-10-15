'''
Author: Kevin Singh

Class to extract attributes from patent XML data, prioritizing certain values.
Handles malformed XML and allows custom XPath and attribute selection.

'''
import numpy as np
import pandas as pd

from cypris_xml_parser import XmlParser

DEFAULT_PRIORITY_ORDER = {
    1: {
        'attribute': "format",
        "values": ["epo"]
    },
    2: {
        'attribute': "load-source",
        "values": ["patent-office"]
    }
}

class PatentAttributeExtractor:
    """
    Extracts attributes from patent XML data.
    """

    def __init__(self, xml_content: str):
        self._xml_data = XmlParser.clean_xml(xml_content)

    def extract_attributes(self, xpath='.//document-id', attributes=None, priority_ordering=None) \
            -> list[str] | pd.DataFrame:
        # convert to df for easier processing
        if priority_ordering is None:
            priority_ordering = DEFAULT_PRIORITY_ORDER
        if attributes is None:
            attributes = ['doc-number']

        df = pd.read_xml(self._xml_data, xpath=xpath)

        # make sure attributes exist in df and priority ordering attributes exist in df
        if not all(attr in df.columns for attr in attributes) and not all(details.get('attribute') in \
                                                                          df.columns for details \
                                                                          in priority_ordering.values()):
            raise ValueError("One or more specified attributes or priority ordering attributes do not exist in the XML data.")

        df.sort_values(by=attributes, inplace=True)

        df['priority'] = np.nan
        if priority_ordering:
            for priority, details in priority_ordering.items():

                attr = details.get('attribute')
                values = details.get('values')
                if attr in df.columns:
                    df['priority'] = df.apply(
                        lambda row: priority if row[attr] in values and pd.isna(row['priority']) else row['priority'],
                        axis=1
                    )

        if len(attributes) == 1:
            return df.sort_values(by=['priority'] + attributes) \
                .drop(columns=['priority']) \
                [attributes[0]] \
                .drop_duplicates() \
                .astype(str) \
                .tolist()

        else:
            return df.sort_values(by=['priority'] + attributes)[attributes]



def main():
    """Main entry point for CLI."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Extract attributes from patent XML documents in priority order.'
    )
    parser.add_argument(
        'xml_file',
        help='Path to the XML file to process'
    )
    parser.add_argument(
        '--xpath',
        default='.//document-id',
        help='XPath to select elements (default: .//document-id)'
    )
    parser.add_argument(
        '--attributes',
        nargs='+',
        default=['doc-number'],
        help='Attributes to extract (default: doc-number)'
    )

    args = parser.parse_args()

    try:
        # Read the XML file
        with open(args.xml_file, 'r', encoding='utf-8') as f:
            xml_data = f.read()

        # Create extractor and extract attributes
        extractor = PatentAttributeExtractor(xml_data)
        result = extractor.extract_attributes(
            xpath=args.xpath,
            attributes=args.attributes
        )

        # Print results
        print("\nExtracted attributes (in priority order):")
        print("=" * 50)
        if isinstance(result, list):
            for i, value in enumerate(result, 1):
                print(f"{i}. {value}")
            print("=" * 50)
            print(f"Total: {len(result)} values extracted")
        else:
            # DataFrame result
            print(result.to_string(index=False))
            print("=" * 50)
            print(f"Total: {len(result)} rows extracted")

    except FileNotFoundError:
        print(f"Error: File '{args.xml_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

