import os
import openai

openai_api_base = os.environ["OPENAI_API_BASE"] 
openai_api_key =os.environ["OPENAI_API_KEY"] 
embedding_model = os.environ['DEPLOYMENT_NAME_EMB']
gpt_model = os.environ["DEPLOYMENT_NAME_GPT"]
deployment_name = os.environ['DEPLOYMENT_NAME_CHAT'] 

openai.api_version = "2023-03-15-preview"
openai.api_type = "azure"
openai.api_base = openai_api_base
openai.api_key = openai_api_key
