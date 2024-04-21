# # To read the PDF
# import pypdf
# # To analyze the PDF layout and extract text
# from pdfminer.high_level import extract_pages, extract_text
# from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# # To extract text from tables in PDF
# import pdfplumber
# # To extract the images from the PDFs
# from PIL import Image
# from pdf2image import convert_from_path
# # To perform OCR to extract text from images
# import pytesseract
# # To remove the additional created files
# import os
# class Parser2:
#
#
#     def __init__(self):
#         print ('initialized')
#
#     def load(self, path):
#
#
#         for pagenum, page in enumerate(extract_pages(path)):
#             print(self.extract_table(path,0,1))
#             # Iterate the elements that composed a page
#             for element in page:
#
#                 # Check if the element is a text element
#                 if isinstance(element, LTTextContainer):
#                     #print(self.text_extraction(element))
#                     # Function to extract text from the text block
#                     pass
#                     # Function to extract text format
#                     pass
#
#                 # Check the elements for images
#                 if isinstance(element, LTFigure):
#                     # Function to convert PDF to Image
#                     pass
#                     # Function to extract text with OCR
#                     pass
#
#                 # Check the elements for tables
#                 if isinstance(element, LTRect):
#                     print(element)
#                     # Function to extract table
#                     pass
#                     # Function to convert table content into a string
#                     pass
#
#     def text_extraction(self, element):
#         # Extracting the text from the in-line text element
#         line_text = element.get_text()
#
#         # Find the formats of the text
#         # Initialize the list with all the formats that appeared in the line of text
#         line_formats = []
#         for text_line in element:
#             if isinstance(text_line, LTTextContainer):
#                 # Iterating through each character in the line of text
#                 for character in text_line:
#                     if isinstance(character, LTChar):
#                         # Append the font name of the character
#                         line_formats.append(character.fontname)
#                         # Append the font size of the character
#                         line_formats.append(character.size)
#         # Find the unique font sizes and names in the line
#         format_per_line = list(set(line_formats))
#
#         # Return a tuple with the text in each line along with its format
#         return (line_text, format_per_line)
#
#     # Extracting tables from the page
#
#     def extract_table(self, pdf_path, page_num, table_num):
#         # Open the pdf file
#         pdf = pdfplumber.open(pdf_path)
#         print(pdf)
#         # Find the examined page
#         table_page = pdf.pages[page_num]
#         print(table_page.extract_tables())
#         # # Extract the appropriate table
#         # table = table_page.extract_tables()[table_num]
#         # return table
#
#     # Convert table into the appropriate format
#     def table_converter(self, table):
#         table_string = ''
#         # Iterate through each row of the table
#         for row_num in range(len(table)):
#             row = table[row_num]
#             # Remove the line breaker from the wrapped texts
#             cleaned_row = [
#                 item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for
#                 item in row]
#             # Convert the table into a string
#             table_string += ('|' + '|'.join(cleaned_row) + '|' + '\n')
#         # Removing the last line break
#         table_string = table_string[:-1]
#         return table_string