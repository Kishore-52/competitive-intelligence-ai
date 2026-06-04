import asyncio
import json
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict

from app.config import config
from app.database import (
    init_db,
    get_all_products,
    add_product,
    delete_product,
    get_all_reports,
    get_report,
    create_empty_report,
    get_chat_history,
    add_chat_message
)
from app.vector_store import vector_store
from app.models import ProductCreate, AnalyzeRequest, ConfigUpdate, ChatMessageCreate
from app.agents.orchestrator import run_pipeline

app = FastAPI(title="Competitive Intelligence Multi-Agent System API")

# Configure CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global map of active SSE log queues: report_id -> asyncio.Queue
active_queues: Dict[int, asyncio.Queue] = {}

@app.on_event("startup")
async def startup_event():
    init_db()
    # Build vector store index from existing DB
    vector_store.rebuild_index()
    print("Database and Vector Store initialized.")

@app.get("/api/config")
def get_config():
    return config.config_data

@app.post("/api/config")
def update_config(settings: ConfigUpdate):
    config.save(settings.dict())
    return config.config_data

@app.get("/api/products")
def list_products():
    return get_all_products()

@app.post("/api/products")
def create_product(product: ProductCreate):
    success = add_product(
        name=product.name,
        description=product.description,
        pricing=product.pricing,
        features=product.features
    )
    if not success:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    # Rebuild Vector Store index to include new product
    vector_store.rebuild_index()
    return {"status": "success", "message": "Product created successfully"}

@app.delete("/api/products/{product_id}")
def remove_product(product_id: int):
    delete_product(product_id)
    vector_store.rebuild_index()
    return {"status": "success", "message": "Product deleted successfully"}

@app.get("/api/reports")
def list_reports():
    return get_all_reports()

@app.get("/api/reports/{report_id}")
def get_report_detail(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.post("/api/reports/analyze")
def trigger_analysis(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    # 1. Create an entry in DB with 'Running' status
    report_id = create_empty_report(req.competitor_name, req.feature_name)
    
    # 2. Create a logs queue for streaming
    log_queue = asyncio.Queue()
    active_queues[report_id] = log_queue
    
    # 3. Trigger the multi-agent orchestrator in the background
    background_tasks.add_task(
        run_pipeline,
        competitor_name=req.competitor_name,
        feature_name=req.feature_name,
        report_id=report_id,
        log_queue=log_queue
    )
    
    return {"status": "running", "report_id": report_id}

@app.get("/api/reports/stream/{report_id}")
async def stream_logs(report_id: int, request: Request):
    """Streams the orchestrator progress logs as Server-Sent Events (SSE)."""
    if report_id not in active_queues:
        # If not active but exists in db, return a done signal
        report = get_report(report_id)
        if report and report["status"] == "Completed":
            async def static_done():
                yield f"data: {json.dumps({'agent': 'Orchestrator', 'status': 'done', 'report_id': report_id, 'message': 'Already complete'})}\n\n"
            return StreamingResponse(static_done(), media_type="text/event-stream")
        raise HTTPException(status_code=404, detail="Active log queue not found for this report")

    queue = active_queues[report_id]

    async def event_generator():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    print(f"Client disconnected from stream {report_id}")
                    break

                try:
                    # Retrieve next log with timeout to prevent hanging forever
                    log_data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(log_data)}\n\n"
                    
                    # If this is the completion log, stop streaming and clean up
                    if log_data.get("status") in ["done", "failed", "error"]:
                        break
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield ": ping\n\n"
        finally:
            # Clean up queue when done
            if report_id in active_queues:
                del active_queues[report_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/reports/{report_id}/chat")
def get_chat(report_id: int):
    return get_chat_history(report_id)

@app.post("/api/reports/{report_id}/chat")
async def ask_report_question(report_id: int, request: ChatMessageCreate):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    user_query = request.message
    
    # Save user message to database
    add_chat_message(report_id, "user", user_query)
    
    # Generate assistant answer
    if config.mock_mode:
        # Intelligent simulated RAG responder using report details
        await asyncio.sleep(1.0)
        answer = generate_mock_chat_response(report, user_query)
    else:
        # Call LLM via LangChain with report context
        try:
            chat_history = get_chat_history(report_id)
            # Compile last 4 messages for conversational context
            history_str = ""
            for msg in chat_history[-5:-1]: # Exclude the user's new message we just added
                history_str += f"{msg['sender'].capitalize()}: {msg['message']}\n"
                
            prompt = f"""
You are a competitive intelligence expert. Answer the user's question about the competitive intelligence report for {report['competitor_name']}'s feature '{report['feature_name']}'.
Use the following report text as your primary context source. Be factual, concise, and focused on strategic suggestions.

REPORT DOCUMENT:
{report['markdown_report']}

CONVERSATION HISTORY:
{history_str}

USER'S QUESTION:
{user_query}

Provide a direct, helpful response. Markdown is encouraged.
"""
            if config.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerAI
                llm = ChatGoogleGenerAI(
                    model=config.gemini_model,
                    google_api_key=config.gemini_api_key,
                    temperature=0.3
                )
                response = await llm.ainvoke(prompt)
                answer = response.content
            else:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=config.openai_model,
                    api_key=config.openai_api_key,
                    temperature=0.3
                )
                response = await llm.ainvoke(prompt)
                answer = response.content
        except Exception as e:
            answer = f"**System Warning:** Failed to connect to LLM API ({str(e)}). Falling back to local responder:\n\n"
            answer += generate_mock_chat_response(report, user_query)
            
    # Save assistant message to database
    add_chat_message(report_id, "assistant", answer)
    
    return {"sender": "assistant", "message": answer}

def generate_mock_chat_response(report: dict, query: str) -> str:
    """Produces intelligent simulated responses from report metadata."""
    q = query.lower()
    comp = report["competitor_name"]
    feat = report["feature_name"]
    threat = report["threat_level"]
    
    # Extract SWOT details
    swot = report["swot"]
    strengths = swot.get("strengths", [])
    weaknesses = swot.get("weaknesses", [])
    opps = swot.get("opportunities", [])
    threats = swot.get("threats", [])
    
    # Extract gaps
    gaps = report["gaps"]
    
    if "pricing" in q or "cost" in q or "price" in q:
        # Look for pricing in markdown or return general answer
        pricing_text = "pricing model is not explicitly detailed in the summaries."
        for line in report["markdown_report"].split("\n"):
            if "pricing" in line.lower() or "price" in line.lower():
                pricing_text = line
                break
        return f"Regarding **{comp} {feat}** pricing, the report highlights:\n\n- It is generally bundled or priced standard.\n- *Source summary:* {pricing_text.replace('*', '')}\n- For our product team, we recommend assessing if we should adjust our standalone pricing or bundle our features to minimize financial threats."
        
    elif "swot" in q or "strength" in q or "weakness" in q or "threat" in q or "opportunity" in q:
        res = f"Here is the SWOT breakdown for **{comp} {feat}** based on our report:\n\n"
        if strengths:
            res += f"**Strengths:**\n" + "\n".join([f"- {s}" for s in strengths]) + "\n\n"
        if weaknesses:
            res += f"**Weaknesses:**\n" + "\n".join([f"- {w}" for w in weaknesses]) + "\n\n"
        if threats:
            res += f"**Threats to Us:**\n" + "\n".join([f"- {t}" for t in threats])
        return res
        
    elif "gap" in q or "compare" in q or "difference" in q or "versus" in q or "vs" in q:
        if not gaps:
            return "No critical feature gaps were identified in the report matrix."
        res = f"Our gap analysis indicates the following items comparing our suite with **{comp} {feat}**:\n\n"
        for idx, g in enumerate(gaps):
            res += f"{idx+1}. **{g.get('category')}** (Severity: **{g.get('severity')}**)\n"
            res += f"   - *Gap:* {g.get('gap_description')}\n"
            res += f"   - *Recommendation:* {g.get('recommendation')}\n\n"
        return res
        
    elif "recommendation" in q or "do" in q or "action" in q or "strategy" in q:
        if not gaps:
            return "The report recommends continuing to monitor competitor releases, maintaining our current pricing structures."
        res = f"The strategic action plan based on the **{comp}** analysis suggests:\n\n"
        for idx, g in enumerate(gaps):
            res += f"- **{g.get('category')} Actions:** {g.get('recommendation')}\n"
        return res
        
    else:
        return f"Thanks for asking! I'm analyzing the report for **{comp} {feat}** (Overall Threat Level: **{threat}**).\n\nBased on the report content, this feature poses significant overlap in terms of team collaboration workflows. If you want specific details, please ask me about:\n- **Pricing** details\n- **SWOT Analysis** (strengths and weaknesses)\n- **Feature Gaps** compared to our products\n- **Strategic Recommendations** for our team"
