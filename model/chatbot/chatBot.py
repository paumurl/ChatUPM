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
from embeddings.embedder import Embedder
from chatbot.similarity import Similarity


class ChatBot:
    def __init__(self):
        """Initialize the ChatBot object.

        Parameters:
            df (DataFrame): The input DataFrame containing the text data.

        """
        self.df = pd.read_pickle("../../data/normativa_embedding_class.pkl")
    
    
    def answer(self, query, terminal=False):
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
        similarity_obj = Similarity(self.df)
        # df = pd.read_pickle('./data/normativa_embeddings.pkl')
        query_emb = Embedder.get_embedding(query)
        df_emb = similarity_obj.df_cosine_similarity(query_emb)

    
        df_emb_tensor = df_emb.sort_values(by='similarity', ascending=False)


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
        
        if terminal == True:
            response_message = "\nBienvenid@ al chatbot de la UPM."
            response_message += f"\n\nPregunta: {query}\n"
            response_message += f'\n{response["choices"][0]["message"]["content"]}'
            source = f"\nPuedes consultar más en {where}.\n"
            response_message += source
            return response_message
        
        else:
            response_message = f'\n{response["choices"][0]["message"]["content"]}'
            source = f"\nPuedes consultar más en {where}."
            response_message += source
            return response_message

        
if __name__ == "__main__":
    query = '¿Cuántos créditos necesito para que no me echen de la UPM?'
    chatupm = ChatBot()
    print(chatupm.answer(query,terminal=True))