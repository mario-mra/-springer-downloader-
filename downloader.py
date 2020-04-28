#!/usr/bin/env python
# Mario Rubio. mrrb.eu.

import urllib.request
import sys
import os

import PyPDF2


filename = 'input.pdf'
if len(sys.argv) == 2:
    filename = sys.argv[1]

## Page URIs
#https://stackoverflow.com/questions/27744210/extract-hyperlinks-from-pdf-in-python
print("Getting page URIs from input pdf...")
PDFFile = open(filename, 'rb')

PDF = PyPDF2.PdfFileReader(PDFFile)
pages = PDF.getNumPages()
key = '/Annots'
uri = '/URI'
ank = '/A'

uris = []
for page in range(pages):
    pageSliced = PDF.getPage(page)
    pageObject = pageSliced.getObject()

    if key in pageObject:
        ann = pageObject[key]
        for a in ann:
            u = a.getObject()
            if uri in u[ank]:
                uris.append(u[ank][uri])

with open('output_uris_page', 'w') as f:
    f.writelines([f"{u}\n" for u in uris])


## PDF URIs
print("Getting download URIs and titles...")
download_uris = []
pdfs_titles = []
base_download_uri = 'http://link.springer.com'

for uri in uris:
    fp = urllib.request.urlopen(uri)
    page = str(fp.read())

    pos1 = page.find('href="/content/pdf/')
    pos2 = page.find('<div data-test="book-title" class="page-title">')

    offset, content1 = 0, []
    for _ in range(2):
        offset += page[pos1+offset:].find('"') + 1
        content1.append(pos1+offset)

    content2 = [pos2+page[pos2:].find('<h1>')+4,
                pos2+page[pos2:].find('</h1>')+1]

    download_uris.append(
        f"{base_download_uri}{page[content1[0]:content1[1]-1]}")
    pdfs_titles.append(f"{page[content2[0]:content2[1]-1]}")

with open('output_uris_pdf', 'w') as f:
    f.writelines([f"{u}\n" for u in download_uris])

with open('output_titles_pdf', 'w') as f:
    f.writelines([f"{u}\n" for u in pdfs_titles])


## PDF download
try:
    os.mkdir('PDFs')
except:
    pass

for index, uri in enumerate(download_uris):
    title = pdfs_titles[index]
    print(
        f"Downloading book #{index+1} of {len(download_uris)}. Title: {title}")
    try:
        file_pdf = open(f"PDFs/{title}.pdf", 'wb')
    except:
        file_pdf = open(f"PDFs/{index}.pdf", 'wb')

    fp = urllib.request.urlopen(uri)
    file_pdf.write(fp.read())

    file_pdf.close()
