# For the scraping
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


class AlumnoParser:
    def __init__(self, url_alumnos, base_url='https://www.upm.es'):
        """Initialize an AlumnoParser object.

        Parameters:
            url_alumnos (str): The URL of the alumnos folder.
            base_url (str): The base URL for parsing.

        """
        self.url_alumnos = url_alumnos
        self.base_url = base_url
        self.html_content = None
        self.pdf_names = []
        self.pdf_elements = []


    def fetch_html(self):
        """Fetch the HTML content of the alumnos folder.

        Returns:
            html_content (bytes): The HTML content.

        """
        try:
            response = requests.get(self.url_alumnos)
            response.raise_for_status()
            self.html_content = response.content
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching content from {self.url_alumnos}: {e}") from e


    def extract_pdf_urls(self):
        """Extract the PDF URLs from the HTML content. Only the latest normatives in admission an enrollment will be retrieved.

        Returns:
            pdf_names,pdf_elements (tuple): A tuple containing the PDF names and their corresponding URLs.

        """
        try:
            # We create the soup object
            soup = BeautifulSoup(self.html_content, 'lxml')
            content_element = soup.find("div", {"class": "content"})
            content_cuerpo = content_element.find('div', attrs={'class': 'cuerpo'})
            ul_elements = content_cuerpo.find_all('ul')

        except AttributeError as e:
            raise Exception(f"Error extracting data from HTML content: {e}") from e
            

        for ul_element in ul_elements:
            # Find the title using BeautifulSoup
            try:
                titles = ul_element.find_all('strong')
            except AttributeError as e:
                raise Exception(f"Error extracting data from HTML content: {e}") from e

            for title_element in titles:
                if title_element and (title_element.text.startswith('Normativa') or title_element.text.startswith('Reglamento')):
                    output_str = title_element.text

                    # Filter <a> elements with href attribute ending with '.pdf'
                    try:
                        pdf_a_elements = [a for a in ul_element.find_all('a') if a.has_attr('href') and a['href'].endswith('.pdf')]
                    except AttributeError as e:
                        raise Exception(f"Error extracting data from HTML content: {e}") from e

                    # Find the latest PDF in the <ul> element
                    if "Curso 2022/2023" in ul_element.text:
                        latest_pdf = [a for a in pdf_a_elements if '/2022_23' in a['href']]
                        if latest_pdf:
                            pdf_name = output_str
                            self.pdf_names.append(pdf_name.replace("\n",""))
                            pdf_url = urljoin(self.base_url, latest_pdf[0]['href'].replace(' ', '%20'))
                            self.pdf_elements.append(pdf_url)
                    else:
                        for a_element in pdf_a_elements:
                            pdf_name = output_str
                            self.pdf_names.append(pdf_name.replace("\n",""))
                            pdf_url = urljoin(self.base_url, a_element['href'].replace(' ', '%20'))
                            self.pdf_elements.append(pdf_url)
