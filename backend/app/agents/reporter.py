import asyncio
import json
from typing import Callable, Dict, List
from app.config import config

MOCK_REPORTS = {
    "slack": {
        "canvas": {
            "swot": {
                "strengths": [
                    "Directly embedded inside Slack's chat UI, removing document retrieval friction.",
                    "Rich integrations allow running Salesforce workflow triggers directly in the canvas.",
                    "Included free in all Slack paid tiers, removing purchasing barriers."
                ],
                "weaknesses": [
                    "Lacks database features (e.g. relational tables, properties) found in Notion.",
                    "Extremely limited styling and layout formatting controls.",
                    "Data is locked inside Slack's ecosystem, creating severe export limitations."
                ],
                "opportunities": [
                    "Allows Slack to position itself as a unified productivity workspace hub.",
                    "Reduces customer dependency on third-party documentation utilities (Confluence/Notion)."
                ],
                "threats": [
                    "Directly threatens Antigravity Docs sales to clients who use Slack.",
                    "Displaces standalone collaborative notes tools in workspace channels."
                ]
            },
            "markdown": """# Competitive Intelligence Report: Slack Canvas Launch

## 1. Executive Summary
On June 3rd, Slack officially rolled out **Slack Canvas**, a new surface in their digital HQ that allows teams to curate, organize, and share information directly in chat workspaces. Canvas provides a wiki-like collaborative document workspace that lives alongside channels and direct messages, enabling users to aggregate text, images, files, links, and rich media.

This launch represents a strategic move by Slack (Salesforce) to expand from communication into document collaboration, directly overlapping with standalone knowledge tools such as Notion, Confluence, and our own **Antigravity Docs**.

**Overall Threat Level: High**
Slack Canvas significantly increases Slack's utility, reducing the need for teams to toggle to external document hubs. For organizations currently utilizing both Slack and Antigravity Docs, Slack Canvas creates a strong incentive to consolidate documentation, risking customer churn.

---

## 2. Competitor Feature Profile
* **Competitor:** Slack (Salesforce)
* **Launched Feature:** Slack Canvas
* **Core Functionality:** Collaborative, block-based documents embedded directly inside Slack channels, user profiles, or standalone canvases.
* **Pricing Model:** Included at no extra cost in Slack Paid Plans (Pro, Business+, Enterprise). Free tier users get access to canvases in 1-on-1 direct messages only.
* **Key Strengths:**
  - Zero-friction access: Toggles open inside a channel sidebar.
  - Interactive canvases: Supports rich media embeds and Slack workflows (e.g., button triggers).
  - Rich chat integration: Canvases can link to specific messages or capture chat threads.

---

## 3. Product Comparison & Gap Analysis
We compared **Slack Canvas** against our own document suite, **Antigravity Docs**:

| Capability / Feature | Slack Canvas | Antigravity Docs | Gap Status & Severity |
| :--- | :--- | :--- | :--- |
| **Document Location** | Embedded directly in chat sidebars and channels | Standalone application web portal | **Gap - High Severity** (Chat integration is more immediate) |
| **Editing Style** | Block-based rich text | Block-based rich text | **Parity** (Both are easy to use) |
| **Interactive Widgets** | Embedded buttons, workflows, live integrations | Static hyperlinks, standard code embeds | **Gap - Medium Severity** (Slack's widgets are actionable) |
| **Database Features** | None (simple lists and blocks) | Relational tables, tags, filtered database views | **Opportunity - High Advantage** (Antigravity is superior for wikis) |

---

## 4. SWOT Analysis

### Strengths
- Deep native collaboration directly inside chat window.
- Bundled into paid licenses, making it 'free' for paying clients.
- Strong support for Salesforce workflow triggers.

### Weaknesses
- Lacks database organization, rollups, or page properties.
- Cannot easily export or share documents outside the Slack workspace.
- No offline support or advanced permission policies for individual headers.

### Opportunities
- Consolidates Slack as the single source of truth for business intelligence.
- Absorbs users who only require lightweight documentation.

### Threats
- Drives consolidation away from dedicated document wikis like ours.
- Diminishes our leverage inside companies that rely heavily on Slack.

---

## 5. Strategic Recommendations

1. **Develop Channel-Level Notes ('Antigravity Canvases'):**
   Introduce a feature in Antigravity Chat that allows pinning a collaborative notes document to any channel. This note should open in a side panel and sync directly with Antigravity Docs, neutralizing Slack's core proximity advantage.
   
2. **Double Down on Database Features:**
   Market Antigravity Docs' database capabilities (which Slack Canvas lacks). Focus marketing efforts on 'structured team wikis', 'project registers', and 'knowledge bases' that require relational data modeling.
   
3. **Build Actionable Widgets:**
   Implement interactive card rendering in Antigravity Docs. For example, pasting a task link from Antigravity Tasks should render as an interactive card where the user can assign, close, or estimate the task directly in the document.
"""
        }
    },
    "zoom": {
        "ai companion": {
            "swot": {
                "strengths": [
                    "Operates natively on call audio/video, providing real-time transcripts and summaries.",
                    "Bundled into paid plans at zero extra cost, disrupting standalone transcriber products.",
                    "Integrated across whiteboards, email replies, and chats."
                ],
                "weaknesses": [
                    "AI summary errors occasionally misattribute actions.",
                    "Lacks repository tools to save, search, and categorize transcripts over long periods."
                ],
                "opportunities": [
                    "Positions Zoom as an all-in-one AI operating suite, expanding out of basic calls."
                ],
                "threats": [
                    "Establishes Zoom as the collector of all meeting tasks, bypassing Antigravity Tasks."
                ]
            },
            "markdown": """# Competitive Intelligence Report: Zoom AI Companion

## 1. Executive Summary
Zoom has officially launched **Zoom AI Companion**, a generative AI assistant integrated natively across its communications software suite. AI Companion generates instant transcripts, summaries, and action plans from live calls, drafts chat replies, and categorizes ideas on Zoom Whiteboards.

This creates significant market changes, as it packages generative meeting tools for free within paid Zoom plans.

**Threat Level: High**
Our users rely on Zoom meetings. By providing native summaries and action items, Zoom threatens to lock in task creations at the meeting source, cutting off **Antigravity Tasks** from the initial sprint planning loop.

---

## 2. SWOT Analysis
* **Strengths:** High proximity, bundled for free, multi-surface integration.
* **Weaknesses:** Occasional inaccuracies, data privacy opt-in requirements, poor long-term organization.
* **Opportunities:** Expanding into administrative workflows.
* **Threats:** Intercepting project plans before they are inputted into project managers like ours.

---

## 3. Strategic Action Plan
1. **API Zoom Integrations:** Build a Zoom app that ingests meeting transcripts into Antigravity Docs, generating synced cards in Antigravity Tasks automatically.
2. **Offline Transcripts:** Market security features: unlike Zoom's cloud AI processing, highlight Antigravity's local encryption standards.
"""
        }
    }
}

def generate_generic_report(competitor: str, feature: str, profile: dict, gaps: list, threat_level: str) -> dict:
    """Generate mock SWOT and Markdown for generic entries."""
    comp_cap = competitor.capitalize()
    
    swot = {
        "strengths": [
            f"Seamless integration into the core {comp_cap} app workspace.",
            "Intuitive UI requiring no additional setup for current clients."
        ],
        "weaknesses": [
            "Relatively basic feature set compared to specialized players.",
            "Lacks advanced custom workflows and extensive reporting formats."
        ],
        "opportunities": [
            "Encourages clients to consolidate operations, saving software licenses.",
            "Establishes a baseline capability that can be expanded in later updates."
        ],
        "threats": [
            "May attract price-sensitive customers looking for bundled services.",
            "Disrupts standalone tools focusing on this specific utility."
        ]
    }
    
    gap_rows = ""
    for g in gaps:
        gap_rows += f"| **{g['category']}** | {g['gap_description']} | **{g['severity']}** | {g['recommendation']} |\n"
        
    markdown = f"""# Competitive Intelligence Report: {comp_cap} Launches {feature}

## 1. Executive Summary
Competitor **{comp_cap}** has launched **{feature}**, a feature aiming to address core workflows in productivity, analytics, and collaboration. This report evaluates its specifications and compares it against our internal product suite.

**Overall Threat Level: {threat_level}**
This feature addresses key workflows that currently drive usage to our platform. We must coordinate engineering and product updates to prevent client attrition.

---

## 2. Competitor Feature Details
* **Description:** {profile.get('feature_description', '')}
* **Pricing Model:** {profile.get('pricing', '')}
* **Target Audience:** {profile.get('target_audience', '')}

---

## 3. Feature Comparison Matrix
We evaluated the gaps between {comp_cap}'s {feature} and our current platform:

| Category | Gap Description | Severity | Action Recommendation |
| :--- | :--- | :--- | :--- |
{gap_rows}

---

## 4. SWOT Summary

* **Strengths:** Direct deployment, zero-friction interface.
* **Weaknesses:** Limited databases, lacks extensive API export scopes.
* **Opportunities:** Serves as a gateway to drive platform loyalty.
* **Threats:** Encroaches on standalone products.

---

## 5. Strategic Next Steps
1. **Accelerate Similar Feature Integrations:** Follow up with features that replicate the competitor's workspace immediacy.
2. **Targeted Product Marketing Campaigns:** Launch advertisements targeting {comp_cap}'s limitations, emphasizing our custom tables, security, and offline support.
"""
    return {"swot": swot, "markdown": markdown}

async def run_reporter(state: Dict, log_callback: Callable[[str, str, str], None]) -> Dict:
    """Compiles findings and writes the final markdown intelligence report."""
    competitor = state.get("competitor_name", "").strip()
    feature = state.get("feature_name", "").strip()
    profile = state.get("competitor_profile", {})
    gaps = state.get("gaps", [])
    threat_level = state.get("threat_level", "Low")
    
    log_callback("Reporter", "active", f"Generating comprehensive intelligence report...")
    await asyncio.sleep(1.0)
    
    if config.mock_mode:
        log_callback("Reporter", "thinking", "Assembling report blocks and drafting SWOT parameters...")
        await asyncio.sleep(2.0)
        
        comp_key = competitor.lower()
        feat_key = feature.lower()
        
        if comp_key in MOCK_REPORTS and feat_key in MOCK_REPORTS[comp_key]:
            results = MOCK_REPORTS[comp_key][feat_key]
        else:
            results = generate_generic_report(competitor, feature, profile, gaps, threat_level)
            
        state["swot"] = results["swot"]
        state["final_report"] = results["markdown"]
    else:
        log_callback("Reporter", "thinking", f"Calling LLM ({config.provider}) via LangChain to compile executive summaries and markdown layout...")
        
        # Build prompt for LLM to output both SWOT JSON and Markdown text
        prompt = f"""
You are a competitive intelligence report generator. Assemble all analytical findings into a formal report and structured SWOT analysis.
Competitor: {competitor}
Feature: {feature}
Overall Threat Level: {threat_level}

Feature Profile:
{json.dumps(profile, indent=2)}

Detected Feature Gaps vs Our Products:
{json.dumps(gaps, indent=2)}

You must return a strict JSON object with EXACTLY two fields:
1. "swot": {{ "strengths": ["..."], "weaknesses": ["..."], "opportunities": ["..."], "threats": ["..."] }}
2. "markdown": "A full, professional Markdown competitive intelligence report. Organize it with headers (Executive Summary, Competitor Feature Profile, Gap Analysis, SWOT Analysis, Strategic Recommendations). Use bullet points and markdown tables for maximum readability. Make it highly executive and factual."

Return ONLY valid JSON.
"""
        try:
            if config.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerAI
                llm = ChatGoogleGenerAI(
                    model=config.gemini_model,
                    google_api_key=config.gemini_api_key,
                    temperature=0.2
                )
                response = await llm.ainvoke(prompt)
                raw_content = response.content
            else:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=config.openai_model,
                    api_key=config.openai_api_key,
                    temperature=0.2
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
            state["swot"] = results["swot"]
            state["final_report"] = results["markdown"]
            log_callback("Reporter", "thinking", "Successfully compiled structured report and SWOT grids.")
        except Exception as e:
            log_callback("Reporter", "warning", f"LLM generation failed ({str(e)}). Falling back to template assembler.")
            results = generate_generic_report(competitor, feature, profile, gaps, threat_level)
            state["swot"] = results["swot"]
            state["final_report"] = results["markdown"]
            await asyncio.sleep(1.0)
            
    log_callback("Reporter", "thinking", "Finalizing formatting and saving to reports database...")
    await asyncio.sleep(0.8)
    
    log_callback("Reporter", "success", "Competitive Intelligence Report compiled successfully.")
    return state
