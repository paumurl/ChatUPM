# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraping.alumnoParser import alumnoParser
from scraping.pdfProcessor import pdfProcessor

class generalScraper:
    def __init__(self):
        """Initialize a generalScraper object using alumnoParser and pdfProcessor classes."""
        self.url_alumnos = 'https://www.upm.es/UPM/NormativaLegislacion/ActuacionesRegulaciones/Grado'
        self.parser = alumnoParser(self.url_alumnos)
        self.pdf_processor = pdfProcessor(self.url_alumnos)

    def to_dataframe(self):
        """Parse the alumnos url, downloads the pdfs and creates a dataframe."""
        dataframe = self.pdf_processor.create_dataframe()
        return dataframe

if __name__ == "__main__":
    df = generalScraper().to_dataframe()
    print(df.head())