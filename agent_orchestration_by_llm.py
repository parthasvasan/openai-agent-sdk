import os
from dotenv import load_dotenv
from agents import Agent, trace, Runner, function_tool
import asyncio
import smtplib
from email.message import EmailMessage

def load_environment():
    load_dotenv(override=True)

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not set!!!")

def create_agent(name, system_prompt, model, tools=[]):
    agent = Agent(
        name=name,
        instructions=system_prompt,
        model=model,
        tools=tools
    )
    return agent

async def run_agent(agent, prompt):
    response = await Runner.run(agent, prompt)
    return response.final_output if response else ''

async def orchestrate_agents(sales_agent1, sales_agent2, sales_agent3, sales_picker_agent):
    sales_manager_prompt = """
    You are a sales manager at company ABC. Your goal is to identify prospective customers by sending cold emails.
    In order to do that, you should use the available tools to generate cold emails, review them, and pick the best email 
    using the sales email picker tool.

    Steps to follow:
    - Generate emails drafts using each of the sales agent tools provided. Instruct each of them to only write an email and no additional content.
    - Ensure all the agents have completed their task and provided you with their draft emails.
    - Now, review them and selct the best email to send using the sales email picker. 
    - Once you have the selected email, use the send email tool to send it.
    """

    description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."
    tools = [
        sales_agent1.as_tool(tool_name="SalesEmailWriter1", tool_description=description),
        sales_agent2.as_tool(tool_name="SalesEmailWriter2", tool_description=description),
        sales_agent3.as_tool(tool_name="SalesEmailWriter3", tool_description=description),
        sales_picker_agent.as_tool(tool_name="SalesEmailPicker", tool_description="Use this tool to review and select the best email from a list of emails provided for the scenario"),
        send_email
    ]
    sales_manager_agent = create_agent(
        "Sales Manager Agent",
        sales_manager_prompt,
        "gpt-5.4-mini",
        tools
    )
    
    with trace("Agent Orchestration By LLM"):
        results = await Runner.run (sales_manager_agent, sales_manager_prompt)
    return results.final_output

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
    sales_agent1 = create_agent(
        name="Sales Agent #1",
        system_prompt="You are a sales agent for a company ABC that produces software for assessing code quality. You write snarky emails to generate new customer leads.",
        model="gpt-5.4-mini"
    )

    sales_agent2 = create_agent(
        name="Sales Agent #2",
        system_prompt="You are a sales agent for a company ABC that produces software for assessing code quality. You write humorous emails to generate new customer leads.",
        model="gpt-5.4-mini"
    )

    sales_agent3 = create_agent(
        name="Sales Agent #3",
        system_prompt="You are a sales agent for a company ABC that produces software for assessing code quality. You write professional emails to generate new customer leads.",
        model="gpt-5.4-mini"
    )

    email_picker_agent = create_agent(
        name="Sales Email Picker Agent",
        system_prompt="You are a helpful assistant capable of reviewing a list o emails provided and pick the best one for the situation.",
        model="gpt-5.4-mini"
    )

    output = asyncio.run(orchestrate_agents(sales_agent1, sales_agent2, sales_agent3, email_picker_agent))
    print(output)


if __name__ == "__main__":
    main()