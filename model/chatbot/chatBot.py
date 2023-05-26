# OpenAI access
import json
import openai

# Basic data management
import numpy as np
import pandas as pd

# Module management
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# The credentials to use Azure OpenAI
from config import *

# Modules from embeddings.py
from embeddings.embedder import embedder
from chatbot.similarity import similarity

# Tensorflow for new embeddings
from silence_tensorflow import silence_tensorflow
silence_tensorflow()
import tensorflow_hub as hub
import tensorflow_text


class chatBot:
    def __init__(self, df):
        """Initialize the ChatBot object.

        Parameters:
            df (DataFrame): The input DataFrame containing the text data.

        """
        self.df = df

    def tensor_embeddings(self, query):
        """Compute the tensor embeddings from the universal-sentence-encoder-multilingual.

        The embeddings are approximately normalized to 1. The inner product is equivalent to the cosine similarities.

        Parameters:
            query (str): The user's query.

        Returns:
            df (DataFrame): The dataframe with an additional 'embeddings_tensor' column containing the tensor embeddings.

        """
        
        self.df['embeddings_tensor'] = pd.Series([None]*len(self.df), dtype='object')
        embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
        embeddings = embed(self.df['chunks'])

        
        for row in range(len(self.df)):
            self.df.at[row, 'embeddings_tensor'] = embeddings[row].numpy()
        
        query_tensor = embed([query])[0].numpy()
        self.df['similarity_tensor'] =''
        self.df['similarity_tensor'] = [np.dot(query_tensor,np.array(i)) for i in self.df['embeddings_tensor']]
        return self.df
    
    
    def answer(self, query, tensor=False):
        """ The final form of our chatbot, that given a query by the user will retrieve the answer given Normativa Alumnos and 
        where to find further info.
        
        Parameters:
            query (string): the user's question we want to provide and answer for.

            tensor (bool, optional): whether to use a multilingual sentence encoder 
                (https://tfhub.dev/google/universal-sentence-encoder-multilingual/3)
                 to create embeddings and use them for the semantic search.

        Returns:
            None

        """
        similarity_obj = similarity(self.df)
        # df = pd.read_pickle('./data/normativa_embeddings.pkl')
        query_emb = embedder.get_embedding(query)
        df_emb = similarity_obj.df_cosine_similarity(query_emb)

        if tensor == False:
            df_emb_tensor = df_emb.sort_values(by='similarity', ascending=False)

        else:
            df_emb_tensor = self.tensor_embeddings(df_emb,query)
            df_emb_tensor = df_emb_tensor.sort_values(by='similarity_tensor', ascending=False)


        introduction = 'Usa la información de debajo para contestar sobre la normativa de la Universidad Politécnica de Madrid. Eres ingenioso y carismático. Responde de forma escueta."'
        question = f"\n\nPregunta: {query}"
        message = introduction
        for string in df_emb_tensor['chunks'].iloc[:3]:
            next_article = f'\n\nSección de la normativa de la UPM:\n"""\n{string}\n"""'
            message += next_article
        message = message + question

        messages = [
            {"role": "system", "content": "Contestas preguntas sobre la normativa de la Universidad Politécnica de Madrid, eres ingenioso y carismático. Responde de forma escueta."},
            {"role": "user", "content": message},
            ]
        response = openai.ChatCompletion.create(
                deployment_id = gpt_model,
                messages = messages,
                temperature = 0.5
            )
        
        where_all = [text for text in df_emb_tensor['normativa'].iloc[:3]]
        where = max(set(where_all), key=where_all.count)
        
        response_message = "\nBienvenid@ al chatbot de la UPM."
        response_message += f"\n\nPregunta: {query}\n"
        response_message += f'\n{response["choices"][0]["message"]["content"]}'
        source = f"\nPuede consultar más en {where}."
        response_message += source
        return print(response_message)


if __name__ == "__main__":
    df = pd.read_pickle("../../data/normativa_embedding_class.pkl")
    query = '¿Cuántos créditos necesito para que no me echen de la UPM?'
    chatupm = chatBot(df)
    chatupm.answer(query)