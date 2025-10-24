from azure.ai.agents.models import FunctionTool

def search_wiki(query:str,search_client) -> str:
    results = search_client.search(query)
    chunks = [doc["text"] for doc in results]
    return "\n\n".join(chunks)



def get_search_tool(search_client):
    # Return a list of callable functions..
    def search_fn(query:str) -> str :
        return search_wiki(query=query, search_client= search_client)
    return FunctionTool([search_fn])
