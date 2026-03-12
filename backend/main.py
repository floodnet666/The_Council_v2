from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from workflow.graph import create_graph
from workflow.graph import create_graph
from utils.logging_config import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from dotenv import load_dotenv
import os

load_dotenv()

# Setup OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
# Export traces to console for now (can be swapped for LangSmith/OTLP)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# Initialize Graph in lifespan
app_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global app_graph
    logger.info("Initializing The Council Agent Graph...")
    app_graph = await create_graph()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="The Council 2.0 API", 
    description="Autonomous AI Analysis System", 
    version="2.0.0",
    lifespan=lifespan
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "active", "system": "The Council 2.0", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    file_path: Optional[str] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    if app_graph is None:
        return {"response": "System is still initializing...", "agent": "system", "status": "error"}

    # Prepare initial state
    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "language": "en",
        "active_file": request.file_path if request.file_path else "",
    }
    
    config = {"configurable": {"thread_id": request.session_id}}
    
    logger.info(f"Processing request: {request.message[:50]}...")
    
    # Run the graph
    try:
        # Contextual log for the entire request
        with logger.contextualize(session_id=request.session_id):
            logger.info("Starting graph execution")
            output = await app_graph.ainvoke(input_state, config=config)
            
            # Get the last message from the last agent
            messages = output["messages"]
            last_message = messages[-1]
            
            logger.info(f"Graph execution complete. Agent: {last_message.name if hasattr(last_message, 'name') else 'unknown'}")
            
            return {
                "response": last_message.content,
                "agent": last_message.name if hasattr(last_message, "name") else "unknown",
                "status": "success"
            }
    except Exception as e:
        with logger.contextualize(session_id=request_session_id):
            logger.error(f"Error processing chat. State: {input_state} | Error: {e}")
            return {"response": "I encountered an error while processing your request.", "agent": "system", "status": "error"}
    

from fastapi import UploadFile, File
import shutil

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Basic security check on filename
    safe_filename = "".join([c for c in file.filename if c.isalnum() or c in "._- "])
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    logger.info(f"Uploading file: {safe_filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": safe_filename, "path": file_path, "status": "uploaded"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
