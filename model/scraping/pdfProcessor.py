# To convert pdfs to text
import requests
import PyPDF2
import re
import io

# Text wrangling
import pandas as pd
import numpy as np

# Time efficiency and optimization
from concurrent.futures import ThreadPoolExecutor

# Import alumnoParser class to scrape the data
from scraping.alumnoParser import AlumnoParser

# Module management
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


class PdfProcessor:
    def __init__(self, url_alumnos="https://www.upm.es/UPM/NormativaLegislacion/ActuacionesRegulaciones/Grado"):
        """Initialize a PDFProcessor object.

        Parameters:
            url_alumnos (str): The URL of the alumnos folder.

        """
        self.url_alumnos = url_alumnos
        self.max_tokens = 2048

    def download_pdf(self, pdf_url):
        """Download a PDF file from a given URL.

        Parameters:
            pdf_url (str): The URL of the PDF file.

        Returns:
            bytes: The content of the downloaded PDF.

        """
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            return response.content
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error downloading PDF from {pdf_url}: {e}") from e

    def extract_text_pdf(self, pdf_content):
        """Extract text from a PDF content.

        Parameters:
            pdf_content (bytes): The content of the PDF file.

        Returns:
            text (str): The extracted text.

        """
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        num_pages = len(pdf_reader.pages)

        text = ' '.join([page.extract_text() for page in pdf_reader.pages])

        text = re.sub(r'\s+',  ' ', text).strip()
        text = re.sub(r". ,","",text)
        text = text.replace(r"..+",".")
        text = text.replace(". .",".")
        text = text.replace("\n", " ")
        text = text.strip()
        return text

    def process_pdf(self, pdf_url):
        """Process a PDF file from the given URL. 
        Downloads the PDF file, extracts its text content, and returns the extracted text.

        Parameters:
            pdf_url (str): The URL of the PDF file.

        Returns:
            text (str): The extracted text from the PDF file.

        """
        pdf_content = self.download_pdf(pdf_url)
        text = self.extract_text_pdf(pdf_content)
        return text

    def split_text(self, text):
        """Split the text into chunks based on a maximum token limit (2046).

        Splits the input text into chunks of tokens, where each chunk has a total token count
        not exceeding the maximum token limit defined in the class.

        Parameters:
            text (str): The input text.

        Returns:
            chunks (list): A list of text chunks.

        """
        tokens = text.split()
        chunks = []

        current_chunk = []
        current_chunk_tokens = 0

        for token in tokens:
            token_length = len(token)

            if current_chunk_tokens + token_length <= self.max_tokens:
                current_chunk.append(token)
                current_chunk_tokens += token_length
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [token]
                current_chunk_tokens = token_length

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def explode_dataframe(self, agg_df):
        """Explode the aggregated dataframe.

        Explodes the given aggregated dataFrame by creating a new dataframe with one row per
        element in the 'chunks' column.

        Parameters:
            agg_df (DataFrame): The aggregated dataframe.

        Returns:
            chunks_df (DataFrame): The exploded dataframe.

        """
        chunks_df = pd.DataFrame({'normativa':'','chunks':''},index=[])
        exploded_df = agg_df.explode('chunks')

        selected_columns_df = exploded_df[['normativa', 'chunks']]

        chunks_df = pd.concat([chunks_df, selected_columns_df], ignore_index=True)
        return chunks_df


    def create_dataframe(self):
        """Create a DataFrame from scraped PDF data.

        Scrapes PDF data using the AlumnoParser, processes the PDFs, and creates a dataframe
        with columns for 'normativa', 'texto', and 'urls'.

        Returns:
            chunks_df (DataFrame): The generated dataframe.

        """
        scraper = AlumnoParser(self.url_alumnos)
        scraper.fetch_html()
        scraper.extract_pdf_urls()
        pdfs_names,pdfs_elements = scraper.pdf_names, scraper.pdf_elements

        text_list = []
        with ThreadPoolExecutor() as executor:
            text_list = list(executor.map(self.process_pdf, pdfs_elements))

        df = pd.DataFrame({'normativa': pdfs_names,'texto': text_list, 'urls': pdfs_elements})

        df_string = df[['normativa', 'texto', 'urls']].astype(str)
        agg_df = df_string.groupby(['normativa']).agg({
            'texto': lambda x: '. '.join(x),
            'urls': lambda x: ', '.join(x)
        }).reset_index()

        agg_df['chunks'] = df['texto'].apply(self.split_text)
        chunks_df = self.explode_dataframe(agg_df)
        chunks_df.to_pickle("../../data/normativa_exploded_class.pkl")

        return chunks_df