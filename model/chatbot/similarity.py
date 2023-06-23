import numpy as np


class Similarity:
    def __init__(self, df):
        """Initialize the Similarity object.

        Parameters:
            df (DataFrame): The input DataFrame containing the text data.

        """
        self.df = df


    def vector_similarity(self, x, y):
        """Calculate the similarity between two vectors.

        Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.

        Parameters:
            x (ndarray): The first vector.
            y (ndarray): The second vector.

        Returns:
            similarity (float): The similarity between the two vectors.

        """
        similarity = np.dot(x, y)
        return similarity 


    def df_cosine_similarity(self, query_emb):
        """Compute cosine similarity between embeddings in the dataframe and the query embedding.

        Parameters:
            query_emb (ndarray): The query embedding.

        Returns:
            df (DataFrame): The dataframe with an additional 'similarity' column containing the cosine similarity scores.

        """
        self.df['similarity'] = ''
        self.df['similarity'] = [self.vector_similarity(query_emb,np.array(i)) for i in self.df['embedding']]
        self.df = self.df.sort_values(by='similarity', ascending=False)
        return self.df
