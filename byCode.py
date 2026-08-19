# import proxy_patch  # uncomment if behind corp proxy (disables SSL verify)
import os
import asyncio
from agents import Agent, ModelSettings, Runner, function_tool, trace
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

script = """
You are a standup comedian, famous for one liners.
You are given a topic and you need to come up with a one line joke about it.
"""

instructions1 = script + "Your topic is corporate management."
instructions2 = script + "Your topic is AI and the future of software development."

comedian1 = Agent(name="agent1", instructions=instructions1, model=OPENAI_MODEL)
comedian2 = Agent(name="agent2", instructions=instructions2, model=OPENAI_MODEL)

message = "Tell a funny joke"

judgement = """
You are a judge, you need to judge the one liner jokes and select the best one.
You are given two jokes and you need to select the best one.
Don't give an explanation; reply with the selected joke only.
Use your tool to print the comedian agent who told the best joke.
"""

@function_tool
def print_joke(agent_name: str):
    """Print the winner of the comedy battle"""
    print(f"Winner:\n{agent_name}") # You can use any tool to send the joke to the user, this is just an example


require_tool = ModelSettings(tool_choice="required")
judge = Agent(name="judge", instructions=judgement,tools=[print_joke],model_settings=require_tool, model=OPENAI_MODEL)


# Orchestration by code
async def judge_jokes():
    with trace("Code Orchestration"):
        commedians=[comedian1, comedian2]
        results = await asyncio.gather(
            Runner.run(comedian1, message),
            Runner.run(comedian2, message),
        )
        outputs = [result.final_output for result in results]

        compiled_jokes = "One Liners:\n\n" + "\n\n".join(
            f"Agent: {agent.name}\nJoke: {output}" for agent, output in zip(commedians, outputs)
        )
        print(compiled_jokes)

        best = await Runner.run(judge, compiled_jokes)

if __name__ == "__main__":
    asyncio.run(judge_jokes())

