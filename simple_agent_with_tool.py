# imports
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, tool, trace
import asyncio
import math

def load_environment():
    load_dotenv (override=True)

    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError ('OPENAI_API_KEY is not set....')

def create_agent(name='Simple Agent', system_prompt='You are a helpful assistant. For any math related question use the calculator_tool to answer.', model='gpt-5.4-mini'):
    return Agent(
        name=name,
        instructions=system_prompt,
        model=model,
        tools=[calculator_tool]
    )

async def run_agent(agent, prompt):
    response = await Runner.run(agent, prompt)
    return response.final_output if response else ''

@function_tool
def calculator_tool(num1: float, num2: float, operator: str):
    """
    Use this tool for any basic mathematical operations - addition, subtraction, division, multiplication
    """
    print (f">>>> calculator_tool called with {num1}, {num2}, and {operator} ...." )
    if not operator or not num1 or not num2:
        raise ValueError ("Invalid parameters to the calculator tool function...")

    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        result = num1 / num2 if num2 != 0 else math.nan
    else:
        return None

def main():
    load_environment()
    agent = create_agent()
    result = asyncio.run(run_agent(agent, 'What is the factorial of 5?'))
    print (result)

if __name__ == '__main__':
    main()