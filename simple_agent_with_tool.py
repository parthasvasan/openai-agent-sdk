# imports
import os
import string
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, tool, trace
import asyncio
import math
import smtplib
from email.message import EmailMessage

def load_environment():
    load_dotenv (override=True)

    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError ('OPENAI_API_KEY is not set....')

def create_agent(name='Simple Agent', system_prompt='You are a helpful assistant. For any math related question use the calculator_tool to calulate the answer. Once completed, use the send_email tool respond with the final answer.', model='gpt-5.4-mini'):
    return Agent(
        name=name,
        instructions=system_prompt,
        model=model,
        tools=[calculator_tool, send_email]
    )

async def run_agent(agent, prompt):
    response = await Runner.run(agent, prompt)
    return response.final_output if response else ''

@function_tool
def calculator_tool(num1: float, num2: float, operator: str) -> float:
    """
    Use this tool for any basic mathematical operations - addition, subtraction, division, multiplication.
    """
    print (f">>>> calculator_tool called with {num1}, {num2}, and {operator} ...." )
    if not operator:
        raise ValueError ("No operator provided to the calculator tool function...")

    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        result = num1 / num2 if num2 != 0 else math.nan
    else:
        raise ValueError ("Unknown operator!!")
    
    return result

@function_tool
def send_email(subject: str, text_body: str, html_body: str):
    """
    Use this tool to send emails to users.
    """
    msg = EmailMessage()
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = os.getenv("EMAIL_ADDRESS")
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(os.getenv("EMAIL_SMTP_SERVER"), 587) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_APP_PASSWORD"))
        server.send_message(msg)

def main():
    load_environment()
    agent = create_agent()
    result = asyncio.run(run_agent(agent, 'What is the factorial of 5?'))
    print (result)

if __name__ == '__main__':
    main()