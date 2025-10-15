"""
Tests for PatentAttributeExtractor class.
"""
import unittest
import pandas as pd
from patent_attribute_extraction import PatentAttributeExtractor, PRIORITY_ORDER


class TestPatentAttributeExtractor(unittest.TestCase):
    """Test cases for PatentAttributeExtractor."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample XML with multiple document-id elements
        self.sample_xml = """<root>
  <application-reference ucid="US-XXXXXXXX-A" is-representative="NO" us-art-unit="9999" us-series-code="">
    <document-id mxw-id="ABCD99999999" load-source="docdb" format="epo">
      <country>US</country>
      <doc-number>999000888</doc-number>
      <kind>A</kind>
      <date>20051213</date>
      <lang>EN</lang>
    </document-id>
    <document-id mxw-id="ABCD88888888" load-source="patent-office" format="original">
      <country>US</country>
      <doc-number>66667777</doc-number>
      <lang>EN</lang>
    </document-id>
  </application-reference>
</root>"""

        # Malformed XML (missing closing brackets)
        self.malformed_xml = """<root>
  <application-reference ucid="US-XXXXXXXX-A" is-representative="NO" us-art-unit="9999" us-series-code
    <document-id mxw-id="ABCD99999999" load-source="docdb" format="epo">
      <country>US</country>
      <doc-number>999000888</doc-number>
      <kind>A</kind>
      <date>20051213</date>
      <lang>EN</lang>
    </document-id>
    <document-id mxw-id="ABCD88888888" load-source="patent-office" format="original">
      <country>US</country>
      <doc-number>66667777</doc-number>
      <lang>EN</lang>
    </document-id>
  </application-reference>
</root>"""

    def test_init_cleans_xml(self):
        """Test that __init__ cleans the XML data."""
        extractor = PatentAttributeExtractor(self.malformed_xml)
        # Should not raise an error
        self.assertIsNotNone(extractor._xml_data)

    def test_extract_single_attribute_default(self):
        """Test extracting single attribute with default parameters."""
        extractor = PatentAttributeExtractor(self.sample_xml)
        result = extractor.extract_attributes()

        # Should return a list
        self.assertIsInstance(result, list)
        # Should contain both doc-numbers
        self.assertEqual(len(result), 2)
        self.assertIn('999000888', result)
        self.assertIn('66667777', result)

    def test_extract_single_attribute_priority_order(self):
        """Test that single attribute extraction respects priority order."""
        extractor = PatentAttributeExtractor(self.sample_xml)
        result = extractor.extract_attributes(priority_ordering=PRIORITY_ORDER)

        # EPO format should come first (999000888)
        # Then patent-office (66667777)
        self.assertEqual(result[0], '999000888')
        self.assertEqual(result[1], '66667777')

    def test_extract_multiple_attributes(self):
        """Test extracting multiple attributes returns DataFrame."""
        extractor = PatentAttributeExtractor(self.sample_xml)
        result = extractor.extract_attributes(
            attributes=['doc-number', 'country', 'lang']
        )

        # Should return a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        # Should have 3 columns
        self.assertEqual(len(result.columns), 3)
        self.assertIn('doc-number', result.columns)
        self.assertIn('country', result.columns)
        self.assertIn('lang', result.columns)
        # Should have 2 rows
        self.assertEqual(len(result), 2)

    def test_extract_with_custom_xpath(self):
        """Test extraction with custom XPath."""
        extractor = PatentAttributeExtractor(self.sample_xml)
        result = extractor.extract_attributes(
            xpath='.//document-id[@format="epo"]'
        )

        # Should only get doc-number from epo format
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], '999000888')

    def test_extract_with_custom_priority_order(self):
        """Test extraction with custom priority ordering."""
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

        extractor = PatentAttributeExtractor(self.sample_xml)
        result = extractor.extract_attributes(priority_ordering=custom_priority)

        # patent-office should come first now (66667777)
        # Then epo (999000888)
        self.assertEqual(result[0], '66667777')
        self.assertEqual(result[1], '999000888')

    def test_malformed_xml_handling(self):
        """Test that malformed XML is handled correctly."""
        extractor = PatentAttributeExtractor(self.malformed_xml)
        result = extractor.extract_attributes()

        # Should still extract the doc-numbers despite malformed XML
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn('999000888', result)
        self.assertIn('66667777', result)

    def test_invalid_attribute_raises_error(self):
        """Test that invalid attributes raise an error."""
        extractor = PatentAttributeExtractor(self.sample_xml)

        with self.assertRaises((ValueError, KeyError)):
            extractor.extract_attributes(attributes=['nonexistent-attribute'])

    def test_empty_xml(self):
        """Test handling of XML with no matching elements."""
        empty_xml = "<root></root>"
        extractor = PatentAttributeExtractor(empty_xml)

        # Should handle gracefully - might raise error or return empty
        try:
            result = extractor.extract_attributes()
            # If it doesn't raise an error, result should be empty
            self.assertEqual(len(result), 0)
        except (ValueError, KeyError):
            # It's acceptable to raise an error for empty XML
            pass


if __name__ == '__main__':
    unittest.main()