import os
from agents import Agent
from dotenv import load_dotenv
import json
from pydantic import BaseModel, Field
from agents import Runner, trace
import asyncio

class EmailMessage(BaseModel):
    subject: str = Field(description="Subject of the email message")
    body: str = Field(description="Body content of the email message")
    recipients: str = Field(description="Comma separated list of recipients for the email messgage")
    sender: str = Field(description="Sender of the email message")

class EmailReview(BaseModel):
    is_professional: bool = Field(description="Indicates whether the email content is written in professional manner or not.")
    review_comments: str = Field(description="Review comments to support the determination if email is professional")

def load_environment():
    load_dotenv(override=True)

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set!!!")

def create_agent(name: str, system_prompt: str, model: str, output_type: BaseModel, tools: list = []):
    return Agent(
        name=name,
        instructions=system_prompt,
        model=model,
        tools=tools,
        output_type=output_type
    )

async def run_agent(agent, prompt):
    result = await Runner.run(agent, prompt)
    return result.final_output

def main():
    load_environment()
    email_agent = create_agent(
        name="Sales_Email_Writer", 
        system_prompt="You are a sales agent for a company ABC that develops code quality product. You write cold emails to prospective customers in a clear, concise, and professional manner with the intention to attract more new customers.",
        model="gpt-5.4-mini",
        output_type=EmailMessage
    )

    output = asyncio.run(run_agent(email_agent, "Write a cold email to a prospective customer."))

    email_review_agent = create_agent(
        name="Sales_Email_Reviewer", 
        system_prompt="You are a sales email review agent. You review the email provided to you and determine if the content is written in a professional manner. Provide your reaoning behind your decision especially in case you determine the email to be un-professional.",
        model="gpt-5.4-mini",
        output_type=EmailReview
    )
    #print(">>>> Output: ", output)
    email_content = f"{output.subject}\n\n{output.body}\n\n"
    response = asyncio.run(run_agent(email_review_agent, f"Review the provided email and determine if it is written in a professional manner. <email>{email_content}</email>"))
    print(response)

if __name__ == "__main__":
    main()