from PyPDF2.pdf import PdfFileReader, PdfFileWriter, PdfFileReader, ContentStream
from PyPDF2.utils import b_
from PyPDF2.generic import FloatObject, NameObject
import argparse

class PDFColorWriter(PdfFileWriter):
    operators = [b_("sc"), b_("rg"), b_("RG"), b_("k"), b_("g")]

    def __init__(self, debug=False):
        PdfFileWriter.__init__(self)
        self.debug = debug

    def toDarkMode(self, pageIndex):
        if pageIndex >= self.getNumPages():
            print(f"Page {pageIndex} does not exist")
            return
        page = self.getPage(pageIndex)
        content = page["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, page.pdf)
        mediabox = page["/MediaBox"]
        backgroundColor = 0x222222
        red = (backgroundColor & 0xFF0000 ) >> (4*4)
        green = (backgroundColor & 0x00FF00 ) >> (4*2)
        blue = (backgroundColor & 0x0000FF )
        operations = [
            ([], b_("q")),
            (list(map(lambda x: FloatObject(x/255), [red, green, blue])), b_("rg")),
            (list(map(lambda x: FloatObject(x), mediabox)), b_("re")),
            ([], b_("f")),
            ([], b_("Q")),
            ([FloatObject(1), FloatObject(1), FloatObject(1)], b_("rg")),
            ([FloatObject(1), FloatObject(1), FloatObject(1)], b_("sc")),
            ([FloatObject(1), FloatObject(1), FloatObject(1)], b_("SC"))
        ]
        content.operations = operations + content.operations
        key = NameObject("/Contents")
        page[key] = content
        page.compressContentStreams()

def replacePDFColor(filepath, outputpath):
    colorReader = PdfFileReader(filepath)
    colorWriter = PDFColorWriter()
    colorWriter.appendPagesFromReader(colorReader)
    for page in range(0, colorWriter.getNumPages()):
        colorWriter.toDarkMode(page)
    outputStream = open(outputpath, "wb")
    colorWriter.write(outputStream)

def main():
    parser = argparse.ArgumentParser(
        description="Scan and swap colors in a PDF file")
    parser.add_argument("input", help="path to input pdf file",
                        type=str)
    
    args = parser.parse_args()
    replacePDFColor(args.input, args.input+'-processed.pdf')
    return 0


if __name__ == "__main__":
    main()
