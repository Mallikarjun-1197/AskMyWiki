from azure.ai.agents.models import FunctionTool
import os
from dotenv import load_dotenv

load_dotenv()

def summarize_text(text: str, openai_client) -> str:
    prompt = f"""Summarize the following wiki content:

    {text}

    Summary:"""
    response = openai_client.chat.completions.create(
        model=os.getenv("GPT_4o_Deployment_Name"),
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_summarize_tool(openai_client):
    # Return a list [] of callable functions.
    def search_fn(query:str) -> str:
        return summarize_text(text=query, openai_client=openai_client)
    return FunctionTool([search_fn])