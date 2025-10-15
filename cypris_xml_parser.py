'''
Author: Kevin Singh

Class to parse and clean XML data, handling  malformations such as missing closing tags,
attributes without values, and placeholder dots

'''
import re

class XmlParser:
    @staticmethod
    def clean_xml(xml_data: str) -> str:
        def fix_attributes_without_values(tag_str: str) -> str:
            """
            Fix attributes that don't have values by adding ="" to them.
            Example: 'us-series-code' was missing a value
            """

            # Match pattern: space followed by the attribute name (no = after it) at the end
            return re.sub(r'\s+([a-zA-Z][a-zA-Z0-9\-_]*)\s*$', r' \1=""', tag_str)

        def fix_malformed_xml_content(xml_str: str) -> str:
            """
            Parse character by character to fix missing '>' brackets.
            When we encounter '<' followed by another '<' before finding '>',
            we insert '>' before the second '<'.
            """
            result = []
            i = 0

            while i < len(xml_str):
                char = xml_str[i]

                # Found start of a tag
                if char == '<':
                    tag_content = '<'
                    i += 1
                    found_closing = False

                    # Read until we find '>' or another '<'
                    while i < len(xml_str):
                        current = xml_str[i]

                        if current == '>':
                            # Normal case - found closing bracket
                            tag_content += current
                            found_closing = True
                            i += 1
                            break
                        elif current == '<':
                            # Found another '<' before closing - malformed!
                            # Fix and add '>'
                            tag_content = fix_attributes_without_values(tag_content)
                            tag_content += '>'
                            found_closing = True
                            # Don't increment i - let outer loop process this '<'
                            break
                        else:
                            tag_content += current
                            i += 1

                    # If we reached end of string without closing
                    if not found_closing:
                        tag_content = fix_attributes_without_values(tag_content)
                        tag_content += '>'

                    result.append(tag_content)
                else:
                    # Regular content
                    result.append(char)
                    i += 1

            return ''.join(result)

        def remove_placeholder_dots(xml_str: str) -> str:
            # remove ... placeholders
            return re.sub(r'\s*\.\.\.\s*', '', xml_str)

        # fix xml content. Eg missing brackets, attributes without values
        xml_data = fix_malformed_xml_content(xml_data)

        # remove placeholder dots
        xml_data = remove_placeholder_dots(xml_data)

        return xml_data
