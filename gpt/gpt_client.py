from openai import AzureOpenAI
import os
from dotenv import  load_dotenv

load_dotenv()


GPT_4o_URL = os.getenv("GPT_4o_URL")
GPT_4o_API_key = os.getenv("GPT_4o_API_key")
GPT_4o_Deployment_Name = os.getenv("GPT_4o_Deployment_Name")
GPT_4o_Version = os.getenv("GPT_4o_Version")

def call_gpt(prompt):
    client = AzureOpenAI(
        azure_endpoint=GPT_4o_URL,
        api_key=GPT_4o_API_key,
        api_version=GPT_4o_Version
    )
    response_stream = client.chat.completions.create(
        model=GPT_4o_Deployment_Name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers based only on the provided context."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    full_response = ""
    for chunk in response_stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            full_response += chunk.choices[0].delta.content
    return full_response.strip()