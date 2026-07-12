import proxy_patch
import os
import asyncio
from agents import Agent, ModelSettings, Runner, function_tool, trace
from dotenv import load_dotenv
from agents.extensions.visualization import draw_graph

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

script = """
You are a standup comedian, famous for one liners.
You are given a topic and you need to come up with a one line joke about it.
"""

instructions1 = script + "Your topic is corporate management."
instructions2 = script + "Your topic is AI and the future of software development."

comedian1 = Agent(name="comedian1", instructions=instructions1, model=OPENAI_MODEL)
comedian2 = Agent(name="comedian2", instructions=instructions2, model=OPENAI_MODEL)

description = "Use this tool to tell a one liner joke. In the input, just instruct it to tell a joke."

comedian_tool1 = comedian1.as_tool(tool_name="joke_teller_1", tool_description=description)
comedian_tool2 = comedian2.as_tool(tool_name="joke_teller_2", tool_description=description)

require_tool = ModelSettings(tool_choice="required")

@function_tool
def print_joke(summary: str):
    """Print the summary of the comedy battle containing both the jokes and the winner"""
    print(f"Summary:\n{summary}") # You can use any tool to send the joke to the user, this is just an example

judgement = """
You are a judge, you need to judge the one liner jokes and select the best one.
Then use your tool to print the jokes and the comedian that told the best joke.
Don't give an explanation; reply with the jokes and the selected winner only.
"""

judge_tools = [print_joke]

judge = Agent(name="judge", instructions=judgement,tools=judge_tools,model_settings=require_tool, model=OPENAI_MODEL)


auditioner_tools = [comedian_tool1, comedian_tool2]



auditioner_instructions = """
You are an auditioner, you need to compile the one liner jokes and send it to the judge.
"""

task = """
Follow these steps:

1. Generate Drafts: Use each of the two joke_teller tools to generate jokes.
Just instruct each to tell a joke; no further details are needed.
Do not proceed until all two jokes are ready, one from each tool.
 
2. Handoff the jokes and the comedians to the judge to choose and print the jokes and the winner.
"""
handohandoffs=[judge]

auditioner = Agent(name="auditioner", instructions=auditioner_instructions,tools=auditioner_tools,model_settings=require_tool,handoffs=handohandoffs, model=OPENAI_MODEL)

async def judge_jokes():
  # Orchestration by LLM, no more calling the agents directly, instead passing them as tools to the judge agent
  with trace("Handoff Orchestration"):
   judge_result = await Runner.run(auditioner, task)

if __name__ == "__main__":
    graph = draw_graph(auditioner)
    graph.view()
    asyncio.run(judge_jokes())
