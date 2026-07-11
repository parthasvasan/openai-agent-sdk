import os
from dotenv import load_dotenv
from agents import Agent, trace, Runner
import asyncio

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
    prompt = "Write a cold sales email to prospective customers"
    with trace("Agent Orchestration By Code"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, prompt),
            Runner.run(sales_agent2, prompt),
            Runner.run(sales_agent3, prompt)
        )

        email_list = "\n\n".join([result.final_output for result in results])

    picker_prompt = f"""
        You are provided a collection of emails from sales agents. Review them as prospective customer and pick the email that 
        you have a high chance to respond to. Respond only with the selected email and no additional content.
        <email list>
        {email_list}
        </email_list>
    """
    final_email = await Runner.run (sales_picker_agent, picker_prompt)
    return final_email.final_output


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