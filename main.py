from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uuid
import os

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "API_KEY.env"))

from agent import run_agent
from Security import is_harmful, is_blacklisted, record_violation
from RAG import retrieve_context

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In memory session store
session_store = {}

# ─────────────────────────────────────────────
# SECURITY MIDDLEWARE
# ─────────────────────────────────────────────
@app.middleware("http")
async def security_labyrinth(request, call_next):
    client_ip = request.client.host
    if client_ip in ["127.0.0.1", "localhost", "::1"]:
        response = await call_next(request)
        return response

    if is_blacklisted(client_ip):
        return JSONResponse(
            status_code=403,
            content={"detail": "Node access revoked."}
        )

    body = await request.body()
    decoded_body = body.decode("utf-8", errors="ignore").lower()

    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive

    if decoded_body and is_harmful(decoded_body):
        record_violation(client_ip)
        return JSONResponse(
            status_code=200,
            content={
                "analysis": "System maintenance in progress.",
                "brief": "Security Node Active."
            }
        )

    response = await call_next(request)
    return response

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Research Assistant is running."}

@app.post("/analyze")
async def analyze(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        # Read uploaded file if provided
        file_content = None
        file_name = None
        if file:
            # VETO: Ensure the file actually has content before reading
            raw = await file.read()
            if raw:
                file_content = raw.decode("utf-8", errors="ignore")
                file_name = file.filename

        # Get RAG context
        rag_context = retrieve_context(question)

        # Run agent
        response = await run_agent(
            user_query=question,
            file_content=file_content,
            rag_context=rag_context
        )

        session_id = str(uuid.uuid4())
        # FIX: Use the 'file_name' variable to avoid NoneType errors
        session_store[session_id] = {
            "query": question,
            "file_content": file_content,
            "file_name": file_name, 
            "rag_context": rag_context,
            "response": response
        }

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Something went wrong: {str(e)}"}
        )

@app.get("/health")
def health():
    return {"status": "ok"}

#test
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)