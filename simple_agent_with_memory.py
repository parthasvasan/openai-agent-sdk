# imports
import os
import random
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, trace
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

async def run_agent(agent, prompt, session=None):
    if session is None:
        response = await Runner.run(agent, prompt)
    else:
        response = await Runner.run(agent, prompt, session=session)
    return response.final_output if response else ''

def main():
    load_environment()
    agent = create_agent()
    session = SQLiteSession (str(random.randint(1, 1000000)), "memory.db")
    result = asyncio.run(run_agent(agent, 'Hi there! My name is Joe. How are you?', session=session))
    print (result)
    result = asyncio.run(run_agent(agent, 'Tell me a fun fact about AI Agents', session=session))
    print (result)
    result = asyncio.run(run_agent(agent, 'What is my name?', session=session))
    print (result)

if __name__ == '__main__':
    main()