# imports
import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace
import asyncio

def load_environment():
    load_dotenv (override=True)

    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError ('OPENAI_API_KEY is not set....')

def create_agent(name='Simple Agent', system_prompt='You are a helpful assistant', model='gpt-5.4-mini'):
    return Agent(
        name=name,
        instructions=system_prompt,
        model=model
    )

async def run_agent(agent, prompt):
    response = await Runner.run(agent, prompt)
    return response.final_output if response else ''

def main():
    load_environment()
    agent = create_agent()
    result = asyncio.run(run_agent(agent, 'Tell me a fun fact about AI Agents'))
    print (result)

if __name__ == '__main__':
    main()