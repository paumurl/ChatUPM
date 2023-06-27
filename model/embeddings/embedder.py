
# OpenAI access
import openai

# Text wrangling, embeddings
import pandas as pd
import numpy as np
import time

# The credentials to use Azure OpenAI
from config import *

# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


class Embedder:
    embedding_model = embedding_model
    def __init__(self, df):
        """Initialize the Embedder object.

        Parameters:
            df (DataFrame): The input DataFrame containing the text data.

        """
        self.df = df

    @staticmethod
    def get_embedding(text, deployment_id=embedding_model):
        """Get numeric vector embeddings for an input text.

        Parameters:
            text (str): The input text to generate embeddings for.
            deployment_id (str, optional): The deployment ID of the embedding model. Defaults to embedding_model in config.py file.

        """
        try:
            result = openai.Embedding.create(deployment_id=deployment_id, input=text)
            result = np.array(result["data"][0]["embedding"])
            return result

        except Exception as e:
            raise Exception(f"Error creating embedding from '{text}': {e}") from e


    def dataframe_embedding(self):
        """ Returns the embedded chunks as a new column in the dataframe. """
        self.df['embedding'] = ''
        num_rows = len(self.df)
        embeddings = [np.nan] * num_rows  # Initialize a list with NaN values

        for i in range(0, num_rows):
            # Apply get_embedding() to the current chunk and store the result in the temporary list
            embeddings[i] = self.get_embedding(self.df.loc[i, 'chunks'])
            
            # Sleep for 1 second, to avoid exceeding call rate limit in the OpenAI S0 pricing tier
            time.sleep(1)

        # Assign the temporary list to the 'embedding' column
        self.df['embedding'] = embeddings
        self.df.to_pickle("../../data/normativa_embedding_class.pkl")
