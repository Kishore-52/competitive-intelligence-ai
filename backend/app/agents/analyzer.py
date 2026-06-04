import asyncio
import json
from typing import Callable, Dict, List
from app.config import config

# High-fidelity mock analysis databases to ensure realistic reports for demo
MOCK_ANALYSIS_BASE = {
    "slack": {
        "canvas": {
            "feature_description": "Slack Canvas is a collaborative, document-style workspace embedded directly inside the Slack chat app. It allows users to write notes, embed videos and files, compile checklist registers, and run Salesforce/Slack workflows directly inside a sidebar pane.",
            "pricing": "Included at no extra cost in Slack Pro, Business+, and Enterprise paid tiers. Free users are limited to direct-message canvases only.",
            "target_audience": "Existing Slack teams, project managers, and organizations looking to reduce app switching between chat and external wikis.",
            "capabilities": [
                "Real-time co-editing of document pages inside the chat sidebar",
                "Frictionless text formatting, bullets, checklists, and header hierarchies",
                "Actionable widgets allowing approval button clicks or Jira ticket updates inside the canvas",
                "Deep messaging integration, converting thread items or messages into canvas components",
                "Rich media embeds (images, files, PDFs, videos, audio clips)"
            ],
            "strengths": [
                "Zero friction: Opens instantly alongside chat, keeping context in one place.",
                "Tight ecosystem connection: Easy to pull files, chats, and users directly into the text surface.",
                "Workflow integration: Can run active Slack/Salesforce workflow buttons."
            ],
            "weaknesses": [
                "Lacks structured databases (unlike Notion's tables and filters).",
                "Limited customizability: No layouts, columns, or complex templates.",
                "Ecosystem lock-in: Extremely hard to share canvases or export data outside Slack."
            ]
        }
    },
    "zoom": {
        "ai companion": {
            "feature_description": "Zoom AI Companion is a generative AI assistant integrated throughout the Zoom communication platform. It summarizes meetings in real-time, extracts key action items, drafts chats and email responses, and brainstorms on Zoom Whiteboards.",
            "pricing": "Included at no additional cost for all paid Zoom user accounts (Pro, Business, Enterprise). Not available on the free tier.",
            "target_audience": "Knowledge workers, managers, and enterprise organizations hosting multiple virtual meetings daily.",
            "capabilities": [
                "Real-time meeting transcription and automatic query handling during calls",
                "AI-generated meeting summaries emailed to participants with categorized action items",
                "Context-aware draft composing for chat responses and post-meeting emails",
                "AI-powered whiteboard generation and sticky-note categorizations",
                "Smart recording segments highlighting speaker changes and topics"
            ],
            "strengths": [
                "High convenience: Automatically emails meeting summaries, saving post-call work.",
                "Free value-add: Packaged at zero extra cost, creating severe friction for third-party AI transcription tools.",
                "Broad utility: Active across chat, email, calls, and whiteboards."
            ],
            "weaknesses": [
                "Summaries can sometimes misattribute action items or summarize general chatter incorrectly.",
                "Privacy concerns: Organizations must explicitly opt-in/opt-out to control how data is used to train models.",
                "Lacks deeper repository storage for long-term knowledge management."
            ]
        }
    },
    "notion": {
        "home": {
            "feature_description": "Notion Home is a personalized hub layout sitting at the top of the Notion sidebar. It serves as a central dashboard that aggregates tasks, calendar schedules, recently opened documents, and database listings into a single visual feed.",
            "pricing": "Included for all Notion users across Free, Plus, Business, and Enterprise plans.",
            "target_audience": "Individual productivity users, project managers, and teams managing multiple separate folders and project boards.",
            "capabilities": [
                "Personalized overview widget showing tasks assigned to the user across all boards",
                "Recent pages widget with fast search and chronological hover list",
                "Trending template recommendations and wiki highlights",
                "Integration widget with Notion Calendar showing daily schedules",
                "Custom greetings and customizable widgets configuration"
            ],
            "strengths": [
                "Reduces navigation clutter: Users see everything they need immediately upon opening the app.",
                "Unifies disparate projects: Collects assignments across multiple independent workspaces.",
                "Encourages team alignment: Highlight feeds pin company-wide guidelines."
            ],
            "weaknesses": [
                "Limited widget customizing options: Users cannot add arbitrary custom HTML/API cards yet.",
                "Overwhelming for users with very small directories who don't need centralized task boards.",
                "Requires using Notion databases for tasks to fully populate the assignment widget."
            ]
        }
    }
}

def generate_generic_analysis(competitor: str, feature: str) -> Dict:
    """Generate structured fallback analysis data for arbitrary competitor features."""
    comp_cap = competitor.capitalize()
    return {
        "feature_description": f"{comp_cap} {feature} is a new productivity-focused capability designed to enhance team efficiency. It embeds interactive workspaces directly inside the existing platform, allowing users to collaborate, aggregate documentation, and automate processes without switching tools.",
        "pricing": f"Available as a premium add-on starting at $5 per user per month, or bundled into {comp_cap}'s Enterprise subscription tier.",
        "target_audience": "Professional operations managers, SaaS users, and enterprise clients seeking process consolidation.",
        "capabilities": [
            "Real-time multi-user editing and comments within the feature interface",
            "Custom automation triggers to link this feature with third-party webhooks",
            "Dynamic dashboards with visual metrics and progress tracking",
            "Advanced file attachment processing and secure access control",
            "A library of starter templates to speed up deployment"
        ],
        "strengths": [
            "Seamless alignment with the existing client environment.",
            "Reduces manual administrative effort through automated trigger rules.",
            "Intuitive, clean UI requiring minimal user onboarding."
        ],
        "weaknesses": [
            "Relatively expensive for small-to-medium business units.",
            "Lacks deep custom charting features for advanced reporting.",
            "Offline functionality is limited, requiring a continuous network connection."
        ]
    }

async def run_analyzer(state: Dict, log_callback: Callable[[str, str, str], None]) -> Dict:
    """Synthesizes scraped competitor web data into a feature profile."""
    competitor = state.get("competitor_name", "").strip()
    feature = state.get("feature_name", "").strip()
    scraped = state.get("scraped_content", [])
    
    log_callback("Analyzer", "active", f"Analyzing feature profile for '{competitor} - {feature}'...")
    await asyncio.sleep(1.0)
    
    # 1. Check if Mock Mode is enabled
    if config.mock_mode:
        log_callback("Analyzer", "thinking", "Analyzing scraped materials and compiling feature dimensions...")
        await asyncio.sleep(1.8)
        
        comp_key = competitor.lower()
        feat_key = feature.lower()
        
        if comp_key in MOCK_ANALYSIS_BASE and feat_key in MOCK_ANALYSIS_BASE[comp_key]:
            profile = MOCK_ANALYSIS_BASE[comp_key][feat_key]
        else:
            profile = generate_generic_analysis(competitor, feature)
            
        state["competitor_profile"] = profile
    else:
        log_callback("Analyzer", "thinking", f"Calling LLM ({config.provider}) via LangChain to analyze scraped details...")
        
        # Prepare context from scraper
        scraped_text = ""
        for i, doc in enumerate(scraped):
            scraped_text += f"\n[Source {i+1}]: {doc['title']} ({doc['url']})\n{doc['snippet']}\n"
            
        prompt = f"""
You are a competitive intelligence analyst. Extract a structured profile of the following competitor feature launch.
Competitor: {competitor}
Feature: {feature}

Search context gathered:
{scraped_text}

Extract the details and return a strict JSON object with EXACTLY the following keys:
{{
  "feature_description": "Detailed multi-sentence summary of the feature, what it does, and how it is integrated.",
  "pricing": "Pricing model, tiers, packages, or if it is included for free.",
  "target_audience": "Description of the target users and customer segments.",
  "capabilities": ["List item 1", "List item 2", ...],
  "strengths": ["Strength 1", "Strength 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...]
}}
Return ONLY valid JSON. No markdown backticks, no comments, no extra text.
"""
        try:
            profile_data = {}
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
                
            # Clean LLM response to get pure JSON
            cleaned_json = raw_content.strip()
            if cleaned_json.startswith("```"):
                # strip code block formatting
                cleaned_json = cleaned_json.split("\n", 1)[1]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json.rsplit("\n", 1)[0]
                cleaned_json = cleaned_json.strip()
                if cleaned_json.startswith("json"):
                    cleaned_json = cleaned_json.split("\n", 1)[1].strip()
                    
            profile_data = json.loads(cleaned_json)
            log_callback("Analyzer", "thinking", "Successfully parsed LLM analysis results.")
            state["competitor_profile"] = profile_data
        except Exception as e:
            log_callback("Analyzer", "warning", f"LLM analysis failed ({str(e)}). Falling back to mock synthesis.")
            state["competitor_profile"] = generate_generic_analysis(competitor, feature)
            await asyncio.sleep(1.0)
            
    # Verify we got a profile
    prof = state["competitor_profile"]
    log_callback("Analyzer", "thinking", f"Extracted core description: \"{prof['feature_description'][:80]}...\"")
    await asyncio.sleep(0.5)
    log_callback("Analyzer", "thinking", f"Identified {len(prof['capabilities'])} capability points.")
    await asyncio.sleep(0.5)
    
    log_callback("Analyzer", "success", f"Competitor feature profile compiled.")
    return state
