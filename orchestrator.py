# orchestrator.py

import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from Tools.search_wiki_tool import get_search_tool
from Tools.summarize_tool import get_summarize_tool
from agent.planner import Planner

def run_orchestration(user_goal: str):
    load_dotenv()

    # Initialize clients
    search_client = SearchClient(
        endpoint=os.getenv("AI_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        credential=AzureKeyCredential(os.getenv("AI_SEARCH_KEY"))
    )

    openai_client = AzureOpenAI(
        api_key=os.getenv("GPT_4o_API_key"),
        api_version=os.getenv("GPT_4o_Version"),
        azure_endpoint=os.getenv("GPT_4o_URL")
    )


    # Register tools
    tools = {
        "SearchWikiTool": get_search_tool(search_client),
        "SummarizeTool": get_summarize_tool(openai_client)
    }

    # Plan
    planner = Planner(openai_client)
    plan = planner.plan(user_goal)
    print(f"Plan : {plan}")
    # Execute
    results = {}
    for i, step in enumerate(plan):
        tool = tools.get(step.get("tool"))
        input_text = step["input"]
        if "step" in input_text.lower():
            ref_index = int("".join(filter(str.isdigit, input_text)))
            input_text = results.get(ref_index - 1, "")
            for func in  tool._functions.values():
                results[i] = func(input_text)
        for func in  tool._functions.values():
                results[i] = func(input_text)

    # Final output
    print("\n📝 Final Output:\n", results[len(plan) - 1])