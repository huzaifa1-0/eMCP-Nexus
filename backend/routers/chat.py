import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from groq import Groq
from backend.db import get_async_session
from backend.ai_services.search_engine import search_tools

router = APIRouter()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))



class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def chat_with_nexus(
    request: ChatRequest, 
    session: AsyncSession = Depends(get_async_session)
):
    """
    RAG Endpoint: 
    1. Searches DB for tools matching the user's message.
    2. Feeds those tools to Llama 3 (Groq) to generate an answer.
    """
    user_query = request.message

    relevant_tools = await search_tools(session, user_query, k=3)
    tools_context = "\n".join(
        [f"- {t.name}: {t.description} (Cost: ${t.cost})" for t in relevant_tools]
    )
    system_prompt = f"""You are NexusAI, a helpful assistant for the eMCP Marketplace.
    User Question: "{user_query}"
    Here are the tools found in our database that might help:
    {tools_context}
    
    If relevant tools are found, recommend them specifically. 
    If no tools match, politely say we don't have that yet.
    Keep answers short and helpful.
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}],
            model="llama-3.3-70b-versatile",
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        print(f"AI Error: {e}")
        return {"response": "I'm having trouble connecting to my brain. Please search manually."}