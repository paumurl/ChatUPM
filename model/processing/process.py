# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


# Import classes
from scraping.generalScraper import GeneralScraper
from embeddings.embedder import Embedder


class Process:
    def run(self):
        """Run the data processing pipeline through GeneralScrapper and Embedder classes.

        Returns:
            pandas.DataFrame: The processed DataFrame with embeddings.

        """
        # Initialize the object
        scraper = GeneralScraper()

        # Scrape the data and get the DataFrame
        df = scraper.to_dataframe()

        # Instantiate the embedder class
        embedder_obj = Embedder(df)

        # Generate the embeddings and get the updated DataFrame
        embedder_obj.dataframe_embedding()

        # Return the final DataFrame
        return embedder_obj.df

if __name__ ==  "__main__":
    dataframe = Process().run()
    print(dataframe)