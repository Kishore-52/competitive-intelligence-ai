import asyncio
import json
from typing import Callable, Dict, List
from app.config import config
from app.vector_store import vector_store

# Pre-seeded mock comparisons for key competitors for demonstration stability
MOCK_COMPARISONS = {
    "slack": {
        "canvas": {
            "threat_level": "High",
            "gaps": [
                {
                    "category": "Workspace Context Proximity",
                    "gap_description": "Slack Canvas is docked directly inside chat channels and sidebars, making it reachable in 1 click. Our product (Antigravity Docs) requires opening a separate tab or application panel, creating a minor friction gap.",
                    "severity": "High",
                    "recommendation": "Implement 'Antigravity Canvas' - a collapsible notes sidebar embedded directly inside Antigravity Chat channels that syncs bi-directionally with Antigravity Docs."
                },
                {
                    "category": "Actionable Chat Widgets",
                    "gap_description": "Slack Canvas allows users to embed active Salesforce/Jira buttons (e.g. 'Approve Budget') that trigger background workflows. Antigravity Docs only supports rich text, links, and basic code blocks.",
                    "severity": "Medium",
                    "recommendation": "Extend Antigravity Docs with interactive widget blocks (e.g., custom button integrations linking to Antigravity Tasks or third-party webhooks)."
                },
                {
                    "category": "Data Management & Databases",
                    "gap_description": "Slack Canvas lacks relational tables, properties, and task database filtering. Antigravity Docs features full-featured relational databases (similar to Notion databases).",
                    "severity": "Low (Product Advantage)",
                    "recommendation": "Emphasize our advanced relational tables in marketing materials. Target teams requiring structured schemas, which Slack Canvas cannot support."
                }
            ]
        }
    },
    "zoom": {
        "ai companion": {
            "threat_level": "High",
            "gaps": [
                {
                    "category": "In-Meeting GenAI Proximity",
                    "gap_description": "Zoom AI Companion operates directly on the audio/video streams in live meetings. Our suite does not have a native video meeting product; we rely on integrations.",
                    "severity": "Critical",
                    "recommendation": "Partner with open-source video tools (e.g. Jitsi) to bundle a lightweight video call solution into Antigravity Chat, pre-integrated with an LLM transcription agent."
                },
                {
                    "category": "Post-Meeting Automation",
                    "gap_description": "Zoom AI Companion emails structured action points and tasks immediately after calls. Antigravity Tasks is decoupled from external meeting notes.",
                    "severity": "Medium",
                    "recommendation": "Build an API listener for Zoom Webhooks. When a Zoom meeting ends, ingest the transcript automatically, parse tasks, and suggest draft items in Antigravity Tasks."
                }
            ]
        }
    },
    "notion": {
        "home": {
            "threat_level": "Medium",
            "gaps": [
                {
                    "category": "Cross-Project Dashboarding",
                    "gap_description": "Notion Home aggregates personal tasks across multiple separate databases onto a single startup tab. In Antigravity Tasks, users must look inside individual project boards or check their email/chat notifications.",
                    "severity": "Medium",
                    "recommendation": "Design a personalized 'Dashboard Hub' at the top of the Antigravity Suite sidebar, compiling a calendar list and task lists from across all project boards."
                }
            ]
        }
    }
}

def generate_generic_comparison(competitor: str, feature: str, retrieved_context: str) -> Dict:
    """Generate mock gap analysis for generic features."""
    return {
        "threat_level": "Medium",
        "gaps": [
            {
                "category": "Automation & Integration",
                "gap_description": f"{competitor.capitalize()} has added deep automation triggers to {feature}, making workflows simple. Our current integrations are primarily static webhooks and manual links.",
                "severity": "Medium",
                "recommendation": "Integrate standard workflow builders into Antigravity Tasks and Chat to support active event triggers."
            },
            {
                "category": "User Experience Friction",
                "gap_description": f"The competitor's implementation of {feature} runs on a highly responsive UI with drag-and-drop capabilities, whereas some elements of our suite require multi-page navigations.",
                "severity": "Medium",
                "recommendation": "Optimize the page transitions and create inline modal popups to handle details rather than loading separate tabs."
            }
        ]
    }

async def run_comparer(state: Dict, log_callback: Callable[[str, str, str], None]) -> Dict:
    """Runs a RAG-based gap analysis against internal products."""
    competitor = state.get("competitor_name", "").strip()
    feature = state.get("feature_name", "").strip()
    profile = state.get("competitor_profile", {})
    capabilities = profile.get("capabilities", [])
    
    log_callback("Comparer", "active", f"Initiating gap analysis against internal product suite...")
    await asyncio.sleep(1.0)
    
    # 1. Gather RAG contexts by querying LocalVectorStore for each capability
    rag_matches = []
    log_callback("Comparer", "thinking", "Querying internal product database via Local Vector Store (RAG)...")
    await asyncio.sleep(1.2)
    
    for cap in capabilities[:3]: # Query using the top capabilities
        matches = vector_store.search(cap, top_k=2)
        for m in matches:
            rag_matches.append(m)
            
    # Deduplicate matches by content
    unique_matches = {}
    for m in rag_matches:
        unique_matches[m["content"]] = m
    deduped_matches = list(unique_matches.values())
    
    # Log retrieved products
    retrieved_products = list(set([m["product_name"] for m in deduped_matches]))
    log_callback("Comparer", "thinking", f"RAG matched {len(deduped_matches)} capabilities from: {', '.join(retrieved_products)}")
    for m in deduped_matches[:3]:
        log_callback("Comparer", "thinking", f"Matched internal feature: {m['content'][:70]}... (Score: {m['score']})")
        await asyncio.sleep(0.4)
        
    # Compile matched contexts into string
    rag_context = ""
    for idx, m in enumerate(deduped_matches):
        rag_context += f"\n[Internal Feature {idx+1}]: {m['content']} (Product: {m['product_name']})\n"
        
    # 2. Perform comparison
    if config.mock_mode:
        log_callback("Comparer", "thinking", "Mock Mode active. Conducting local comparative analysis...")
        await asyncio.sleep(1.8)
        
        comp_key = competitor.lower()
        feat_key = feature.lower()
        
        if comp_key in MOCK_COMPARISONS and feat_key in MOCK_COMPARISONS[comp_key]:
            results = MOCK_COMPARISONS[comp_key][feat_key]
        else:
            results = generate_generic_comparison(competitor, feature, rag_context)
            
        state["threat_level"] = results["threat_level"]
        state["gaps"] = results["gaps"]
    else:
        log_callback("Comparer", "thinking", f"Calling LLM ({config.provider}) via LangChain to compile threat levels & gap matrix...")
        
        prompt = f"""
You are a competitive intelligence systems analyst. Compare the following competitor feature capabilities against our internal product features (RAG contexts).
Competitor: {competitor}
Feature: {feature}

Competitor Capabilities:
{json.dumps(capabilities, indent=2)}

Our Matched Product Features (from RAG vector search):
{rag_context}

Identify any feature gaps. Detail how their feature differs, and provide concrete, actionable recommendations for our engineering/product teams to catch up or capitalize on advantages.
Return a strict JSON object with EXACTLY the following format:
{{
  "threat_level": "Low | Medium | High | Critical",
  "gaps": [
    {{
      "category": "Feature area (e.g. Collaboration, Analytics, Mobile, UI Proximity)",
      "gap_description": "Explanation of the gap between their feature capability and ours.",
      "severity": "Low | Medium | High | Critical",
      "recommendation": "Actionable product/engineering advice to close the gap."
    }},
    ...
  ]
}}
Return ONLY valid JSON.
"""
        try:
            if config.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerAI
                llm = ChatGoogleGenerAI(
                    model=config.gemini_model,
                    google_api_key=config.gemini_api_key,
                    temperature=0.1
                )
                response = await llm.ainvoke(prompt)
                raw_content = response.content
            else:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=config.openai_model,
                    api_key=config.openai_api_key,
                    temperature=0.1
                )
                response = await llm.ainvoke(prompt)
                raw_content = response.content
                
            cleaned_json = raw_content.strip()
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json.split("\n", 1)[1]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json.rsplit("\n", 1)[0]
                cleaned_json = cleaned_json.strip()
                if cleaned_json.startswith("json"):
                    cleaned_json = cleaned_json.split("\n", 1)[1].strip()
                    
            results = json.loads(cleaned_json)
            log_callback("Comparer", "thinking", "Successfully parsed LLM comparison results.")
            state["threat_level"] = results["threat_level"]
            state["gaps"] = results["gaps"]
        except Exception as e:
            log_callback("Comparer", "warning", f"LLM comparison failed ({str(e)}). Falling back to mock comparison.")
            results = generate_generic_comparison(competitor, feature, rag_context)
            state["threat_level"] = results["threat_level"]
            state["gaps"] = results["gaps"]
            await asyncio.sleep(1.0)

    log_callback("Comparer", "thinking", f"Calculated Threat Level: {state['threat_level']}")
    await asyncio.sleep(0.5)
    log_callback("Comparer", "thinking", f"Identified {len(state['gaps'])} product gap areas.")
    await asyncio.sleep(0.5)
    
    log_callback("Comparer", "success", "Product gap analysis complete.")
    return state
