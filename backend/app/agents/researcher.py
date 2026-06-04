import asyncio
import json
from typing import Callable, Dict, List
from app.config import config

# High-quality mock articles databases for key competitors to guarantee a flawless experience
MOCK_INTELLIGENCE_BASE = {
    "slack": {
        "canvas": [
            {
                "url": "https://slack.com/blog/news/slack-canvas-now-available-to-all-teams",
                "title": "Slack Canvas: A New Way to Curate and Share Information in Your Digital HQ",
                "snippet": "Slack Canvas is a new surface in Slack that lets teams curate, organize, and share information. Canvases can contain text, files, links, media, and even rich embeds of workflows. Canvases are now rolling out to all Slack customers."
            },
            {
                "url": "https://techcrunch.com/2023/05/03/slack-rolls-out-canvases-for-collaborative-documents-in-chats/",
                "title": "Slack rolls out Canvases for collaborative documents in chats",
                "snippet": "Slack is releasing Canvas, a feature first announced last year, which gives teams a dedicated space to write down notes, embed images/videos, and link channels. Paid plans get unlimited canvases, while free plans get canvases in direct messages."
            },
            {
                "url": "https://www.theverge.com/2023/5/3/23709605/slack-canvas-collaborative-notes-features-release-date",
                "title": "Slack Canvas is here to kill your team's document clutter",
                "snippet": "Slack is rolling out Canvas, a wiki-style document editor built directly into its channels. Canvases make it easy for teams to capture notes, spreadsheets, meeting agendas, and task checklists without leaving the chat interface."
            }
        ]
    },
    "zoom": {
        "ai companion": [
            {
                "url": "https://blog.zoom.us/zoom-ai-companion-announcement/",
                "title": "Introducing Zoom AI Companion, Your New Generative AI Assistant",
                "snippet": "Zoom AI Companion is a generative AI assistant that is included at no additional cost with paid Zoom user accounts. It helps users summarize meetings, compose emails, draft chat replies, and brainstorm ideas in Zoom Whiteboards."
            },
            {
                "url": "https://www.zdnet.com/article/zoom-unveils-ai-companion-to-summarize-meetings-and-draft-responses/",
                "title": "Zoom unveils AI Companion to summarize meetings, draft emails",
                "snippet": "Zoom has launched Zoom AI Companion, a generative AI assistant. It provides real-time meeting summarization, query support during live meetings, action item extraction, and draft generation for emails and team chats. Included with paid plans."
            }
        ]
    },
    "notion": {
        "home": [
            {
                "url": "https://www.notion.so/blog/introducing-notion-home",
                "title": "Introducing Notion Home: A Dedicated Space for Your Day",
                "snippet": "Notion Home is a brand new central dashboard that aggregates your tasks, recent docs, templates, and calendar events in one place. It gives users a personalized overview of their workday and helps them jump back into active workflows."
            },
            {
                "url": "https://techcrunch.com/2024/02/notion-adds-home-tab-and-calendar-integrations/",
                "title": "Notion adds personalized 'Home' tab to combat workplace tool chaos",
                "snippet": "Notion has launched Home, a dashboard page that sits at the top of the sidebar. It displays a user's recent pages, tasks assigned to them, daily schedules, and recommended templates, reducing navigation clicks."
            }
        ]
    }
}

def generate_generic_mock_data(competitor: str, feature: str) -> List[Dict[str, str]]:
    """Generate detailed mock search results for any arbitrary competitor feature."""
    comp_lower = competitor.capitalize()
    feat_lower = feature.lower()
    return [
        {
            "url": f"https://www.techcrunch.com/news/{competitor.lower()}-{feature.replace(' ', '-')}-launch",
            "title": f"{comp_lower} Launches New {feature} Feature to Streamline Team Workflows",
            "snippet": f"In a major product update, {comp_lower} has officially unveiled '{feature}', a new tool designed to enhance user productivity. The update features seamless workspace integrations, advanced search filters, and real-time collaboration widgets. Analysts see this as a direct challenge to alternative SaaS platforms."
        },
        {
            "url": f"https://blog.{competitor.lower()}.com/introducing-{feature.replace(' ', '-')}",
            "title": f"Introducing {feature}: Elevating the {comp_lower} Experience",
            "snippet": f"Today we are thrilled to announce the general availability of {feature} on {comp_lower}. Built from the ground up to address user feedback, {feature} allows teams to easily manage complex projects, customize layouts, and trigger automated tasks. This features is rolling out globally over the next few weeks."
        },
        {
            "url": f"https://www.producthunt.com/posts/{competitor.lower()}-{feature.replace(' ', '-')}",
            "title": f"{comp_lower} {feature} on Product Hunt",
            "snippet": f"A brand new way to handle product updates on {comp_lower}. Features include native desktop notifications, drag-and-drop components, customizable dashboards, and collaborative sharing links. Pricing starts on their standard tiers, with a free trial available."
        }
    ]

async def run_researcher(state: Dict, log_callback: Callable[[str, str, str], None]) -> Dict:
    """Gathers competitor product/feature search data."""
    competitor = state.get("competitor_name", "").strip()
    feature = state.get("feature_name", "").strip()
    
    log_callback("Researcher", "active", f"Initializing research for '{competitor}' feature: '{feature}'...")
    await asyncio.sleep(1.2)
    
    query = f"{competitor} {feature} launch pricing reviews features"
    state["search_queries"] = [query]
    log_callback("Researcher", "thinking", f"Constructing search query: \"{query}\"")
    await asyncio.sleep(1.0)
    
    scraped_data = []
    
    # Check if we should use mock or real search
    if config.mock_mode:
        log_callback("Researcher", "thinking", "Mock Mode is enabled. Retrieving pre-seeded data from Intelligence Base...")
        await asyncio.sleep(1.5)
        
        comp_key = competitor.lower()
        feat_key = feature.lower()
        
        if comp_key in MOCK_INTELLIGENCE_BASE and feat_key in MOCK_INTELLIGENCE_BASE[comp_key]:
            scraped_data = MOCK_INTELLIGENCE_BASE[comp_key][feat_key]
        else:
            log_callback("Researcher", "thinking", f"No specific pre-seeded data for '{competitor} {feature}'. Generating custom context...")
            scraped_data = generate_generic_mock_data(competitor, feature)
            await asyncio.sleep(1.0)
    else:
        log_callback("Researcher", "thinking", f"Mock Mode is disabled. Querying DuckDuckGo Search for live updates...")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                ddgs_gen = ddgs.text(query, max_results=4)
                results = list(ddgs_gen)
                
            if results:
                for idx, r in enumerate(results):
                    scraped_data.append({
                        "url": r.get("href", ""),
                        "title": r.get("title", ""),
                        "snippet": r.get("body", "")
                    })
                log_callback("Researcher", "thinking", f"DuckDuckGo search successful. Retrieved {len(scraped_data)} web results.")
            else:
                log_callback("Researcher", "warning", "DuckDuckGo search returned 0 results. Falling back to simulator.")
                scraped_data = generate_generic_mock_data(competitor, feature)
        except Exception as e:
            log_callback("Researcher", "warning", f"DuckDuckGo search failed ({str(e)}). Falling back to simulator.")
            scraped_data = generate_generic_mock_data(competitor, feature)
            await asyncio.sleep(1.0)
            
    # Process scraped data
    state["scraped_content"] = scraped_data
    
    # Log findings summary
    for r in scraped_data:
        log_callback("Researcher", "thinking", f"Processed source: {r['title']} ({r['url']})")
        await asyncio.sleep(0.5)
        
    log_callback("Researcher", "success", f"Gathered {len(scraped_data)} relevant articles and pages.")
    return state
