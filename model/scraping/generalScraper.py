# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraping.alumnoParser import AlumnoParser
from scraping.pdfProcessor import PdfProcessor

class GeneralScraper:
    def __init__(self):
        """Initialize a GeneralScraper object using AlumnoParser and PdfProcessor classes."""
        self.url_alumnos = 'https://www.upm.es/UPM/NormativaLegislacion/ActuacionesRegulaciones/Grado'
        self.parser = AlumnoParser(self.url_alumnos)
        self.pdf_processor = PdfProcessor(self.url_alumnos)

    def to_dataframe(self):
        """Parse the alumnos url, downloads the pdfs and creates a dataframe."""
        dataframe = self.pdf_processor.create_dataframe()
        return dataframe

if __name__ == "__main__":
    df = GeneralScraper().to_dataframe()
    print(df.head())