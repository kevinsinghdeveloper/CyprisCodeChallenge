from patent_attribute_extraction import PatentAttributeExtractor, PRIORITY_ORDER

with open('input_xmls/test_case_1.txt', 'r') as f:
    xml_data = f.read()

# Create extractor
extractor = PatentAttributeExtractor(xml_data)

# Extract doc-numbers with default priority (EPO first, then patent-office)
doc_numbers = extractor.extract_attributes(priority_ordering=PRIORITY_ORDER)
print(doc_numbers)

