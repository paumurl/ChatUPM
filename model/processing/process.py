# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


# Import classes
from scraping.generalScraper import generalScraper
from embeddings.embedder import embedder


class process:
    def run(self):
        """Run the data processing pipeline through generalScrapper and embedder classes.

        Returns:
            pandas.DataFrame: The processed DataFrame with embeddings.

        """
        # Initialize the object
        scraper = generalScraper()

        # Scrape the data and get the DataFrame
        df = scraper.to_dataframe()

        # Instantiate the embedder class
        embedder_obj = embedder(df)

        # Generate the embeddings and get the updated DataFrame
        df_with_embeddings = embedder_obj.dataframe_embedding()

        # Return the final DataFrame
        return df_with_embeddings

if __name__ ==  "__main__":
    dataframe = process().run()
    print(dataframe)