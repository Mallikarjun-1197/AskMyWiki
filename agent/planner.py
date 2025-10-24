import json
import os
from dotenv import load_dotenv

load_dotenv()


class Planner:
    def __init__(self,gpt_client):
        self.gpt_client = gpt_client

    def plan_task(self, user_query):
        prompt = f"""
You are a planning agent. Break down the user's goal into 2–5 actionable steps that can be answered using wiki content.

User goal: "{user_query}"

Respond with a numbered list of steps.
"""
        print("\n🧠 Planning agent prompt:\n", prompt)
        print("\n🧭 Agent Plan:\n")
        return self.gpt_client(prompt)

    def plan(self, user_goal: str) -> list:
        prompt = f"""
    You are a planner agent. Your job is to break down the user's goal into steps and assign each step to a tool.

    Available tools:
    - SearchWikiTool: retrieves wiki content based on a query
    - SummarizeTool: summarizes text into a concise answer
    Use precise queries that retrieve only the most relevant wiki content. Avoid overly broad terms
    Respond only with a raw JSON array of steps. Do not include any markdown, explanation, or formatting. Example:
    [
        {{ "step": "Find onboarding checklist", "tool": "SearchWikiTool", "input": "onboarding checklist" }},
        {{ "step": "Summarize checklist", "tool": "SummarizeTool", "input": "chunk text from step 1" }}
    ]


    User goal: {user_goal}
    """
        response = self.gpt_client.chat.completions.create(
            model=os.getenv("GPT_4o_Deployment_Name"),
            messages=[{"role": "user", "content": prompt}]
        )
        # print(f"Response from planner : {response}")
        return json.loads(response.choices[0].message.content)
