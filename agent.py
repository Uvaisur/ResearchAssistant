from pydantic import BaseModel, Field
from pydantic_ai import Agent
from dotenv import load_dotenv
from pydantic_ai.models.google import GoogleModel
import asyncio
import os

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "API_KEY.env"))

model = GoogleModel("gemini-2.5-flash-lite")

class rsrfile(BaseModel):
    doc: str = Field(description="Research file for analysis and first principle thinking")

Assistant = Agent(
    model,
    system_prompt=(
        "You are a scientist obsessed with root causes and pattern analysis.\n"
        "Your tasks:\n"
        "1. Analyze the user query along with research file if provided.\n"
        "2. Break the elements of the user query into basics.\n"
        "3. Provide a detailed report on the query using first principles thinking\n"
        "4. Show how elements interact with the everyday world and generate ideas.\n"
        "5. Format your response as plain text only, No markdown, no asterisks, no hashtags, no special characters.\n"
        "6. If research file is not provided, stick with simple answers for query using first principle thinking"
    ),
    output_type=rsrfile
)

async def run_agent(user_query: str, file_content: str = None, rag_context: str = None) -> str:
    message_parts = []

    # File content passed directly as string
    if file_content:
        message_parts.append(f"Here is the uploaded document:\n\n{file_content}")

    # RAG context
    if rag_context:
        message_parts.append(f"Here is the relevant research context:\n\n{rag_context}")

    # User query
    message_parts.append(f"User question: {user_query}")

    user_message = "\n\n".join(message_parts)
    result = await Assistant.run(user_message)
    return result.output.doc.replace("\\n", "\n").replace("\n", " ").strip()


# Standalone test
if __name__ == "__main__":
    async def test():
        response = await run_agent(
            user_query="what do you think about US Israel-Iran war?",
        )
        print(response)

    asyncio.run(test())