from agent.planner import Planner
from search.searcher import search

class WikiAgent:
    def __init__(self, gpt_client, env=None):
        self.env = env
        self.planner = Planner(gpt_client)

    def run(self, user_query):
        print(f"\n🧠 User query: {user_query}")
        
        plan = self.planner.plan_task(user_query)
        if not plan or not isinstance(plan, str):
            print("⚠️ Planner returned no steps. Skipping retrieval.")
            return []

        # print(f"\n🧭 Agent Plan:\n{plan}")

        results = []
        for step in plan.split("\n"):
            step = step.strip()
            if not step:
                continue

            # print(f"\n🔍 [Step] {step}")
            chunks = search(step)  # If your search() needs env, pass it: search(step, self.env)

            print(f"📚 Retrieved {len(chunks)} chunks for: {step}")
            for i, chunk in enumerate(chunks):
                # print(f"\nChunk {i+1}:")
                print(f"Section: {chunk.get('section')}")
                print(f"Filename: {chunk.get('filename')}")
                # print(f"Text: {chunk.get('text')[:300]}...")  # First 300 chars
                # print(f"URL: {chunk.get('url')}")

            results.append((step, chunks))

        return results