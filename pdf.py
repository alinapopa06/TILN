from tika import parser
import json

raw = parser.from_file(r"C:\Users\alina\Desktop\byte\articole ok\21.pdf")
#print(raw['content'])
file1 = open(r"C:\Users\alina\Desktop\byte\0.txt","w",encoding='utf-8')
str(raw).replace('x','')
file1.write(str(raw).replace('\\n','\n'))
file1.close()

# import pdftotext
#
# # Load your PDF
# with open("Target.pdf", "rb") as f:
#     pdf = pdftotext.PDF(f)
#
# # Save all text to a txt file.
# with open('output.txt', 'w') as f:
#     f.write("\n\n".join(pdf))


# from PyPDF2 import PdfFileReader
# import re
#
# def extract_information(pdf_path):
#     with open(pdf_path, 'rb') as f:
#         pdf = PdfFileReader(f, strict=False)
#         information = pdf.getDocumentInfo()
#         number_of_pages = pdf.getNumPages()
#         for page in range(number_of_pages):
#             print(pdf.getPage(page).extractText())
#
#     txt = f"""
#     Information about {pdf_path}:
#
#     Author: {information.author}
#     Creator: {information.creator}
#     Producer: {information.producer}
#     Subject: {information.subject}
#     Title: {information.title}
#     Number of pages: {number_of_pages}
#     """
#
#     print(txt)
#     return information
#
# if __name__ == '__main__':
#     path = 'salut2.pdf'
#     extract_information(path)
#
