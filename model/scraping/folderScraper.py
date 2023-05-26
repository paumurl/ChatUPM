# For the scraping
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


class folderScraper:
    def __init__(self, url):
        """Initialize a FolderScraper object.

        Parameters:
            url (str): The URL of the normatives folder.

        """
        self.url = url

    def get_folders(self):
        """ Given the UPM url of normatives (https://www.upm.es/UPM/NormativaLegislacion/LegislacionNormativa), 
        it will return the urls of all the subfolders.
        
        Parameters:
            url (string): the UPM url of all normatives.

        Returns:
            url_embeddings (list): a list of all the urls belonging to the UPM normative subfolders.

        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error extracting data from HTML content: {e}") from e
            
    
        html_content = response.content
        soup = BeautifulSoup(html_content, 'lxml')

        try:
            content_element = soup.find("div", {"id": "contenido"})
            content_div = content_element.find('div', attrs={'class': 'content'})
            nuevo = content_div.find_all('a', attrs={'class': 'links-unico'})
        
        except AttributeError as e:
            raise Exception(f"Error extracting data from HTML content: {e}") from e
            
        urls_embeddings = [urljoin(self.url, a['href'].replace(" ", "%20")) for a in nuevo]
        return urls_embeddings
