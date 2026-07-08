# imports
import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace
import asyncio

from openai.types.responses import ResponseTextDeltaEvent

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
    response = Runner.run_streamed(agent, input=prompt)
    async for event in response.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
            and event.data.delta
        ):
            print(event.data.delta, end='', flush=True)
    print()

def main():
    load_environment()
    agent = create_agent()
    asyncio.run(run_agent(agent, 'Describe what an agent framework is'))

if __name__ == '__main__':
    main()