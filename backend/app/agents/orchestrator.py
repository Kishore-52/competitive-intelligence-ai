import asyncio
import json
import traceback
from typing import Dict
from app.database import update_report_results, update_report_status
from app.agents.researcher import run_researcher
from app.agents.analyzer import run_analyzer
from app.agents.comparer import run_comparer
from app.agents.reporter import run_reporter

async def run_pipeline(competitor_name: str, feature_name: str, report_id: int, log_queue: asyncio.Queue):
    """Coordinates and executes the multi-agent intelligence pipeline."""
    state = {
        "competitor_name": competitor_name,
        "feature_name": feature_name,
        "scraped_content": [],
        "competitor_profile": {},
        "gaps": [],
        "threat_level": "Low",
        "swot": {},
        "final_report": ""
    }

    def log_callback(agent: str, status: str, message: str):
        """Pushes structured status updates to the streaming queue."""
        asyncio.create_task(log_queue.put({
            "agent": agent,
            "status": status,
            "message": message
        }))

    try:
        # Step 1: Research Agent
        log_callback("Orchestrator", "active", "Kicking off research agent...")
        state = await run_researcher(state, log_callback)
        await asyncio.sleep(0.5)

        # Step 2: Analyzer Agent
        log_callback("Orchestrator", "active", "Deploying feature analysis agent...")
        state = await run_analyzer(state, log_callback)
        await asyncio.sleep(0.5)

        # Step 3: Comparer Agent (RAG)
        log_callback("Orchestrator", "active", "Initializing comparison & gap analysis agent...")
        state = await run_comparer(state, log_callback)
        await asyncio.sleep(0.5)

        # Step 4: Reporter Agent
        log_callback("Orchestrator", "active", "Initializing report synthesis agent...")
        state = await run_reporter(state, log_callback)
        await asyncio.sleep(0.5)

        # Step 5: Save results to database
        log_callback("Orchestrator", "active", "Saving generated intelligence report to database...")
        
        # Pull sources
        sources = [s.get("url", "") for s in state.get("scraped_content", [])]
        
        update_report_results(
            report_id=report_id,
            threat_level=state["threat_level"],
            swot=state["swot"],
            gaps=state["gaps"],
            markdown_report=state["final_report"],
            sources=sources
        )
        
        log_callback("Orchestrator", "success", "Report compiled and persisted successfully!")
        
        # Tell the UI we are complete and provide the report ID
        await log_queue.put({
            "agent": "Orchestrator",
            "status": "done",
            "report_id": report_id,
            "message": "Pipeline completed successfully."
        })

    except Exception as e:
        error_msg = f"Orchestration failure: {str(e)}"
        print(f"Error running pipeline: {error_msg}")
        traceback.print_exc()
        
        # Update database status to Failed
        try:
            update_report_status(report_id, "Failed")
        except Exception:
            pass
            
        log_callback("Orchestrator", "error", error_msg)
        await log_queue.put({
            "agent": "Orchestrator",
            "status": "failed",
            "message": error_msg
        })
