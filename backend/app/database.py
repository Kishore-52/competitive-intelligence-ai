import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        pricing TEXT,
        features TEXT, -- JSON array of feature descriptions
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor_name TEXT NOT NULL,
        feature_name TEXT NOT NULL,
        threat_level TEXT NOT NULL, -- Low, Medium, High, Critical
        status TEXT NOT NULL, -- Running, Completed, Failed
        swot TEXT, -- JSON object: {strengths: [], weaknesses: [], opportunities: [], threats: []}
        gaps TEXT, -- JSON array of feature gap objects
        markdown_report TEXT,
        sources TEXT, -- JSON array of strings
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Chat history table for reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        sender TEXT NOT NULL, -- user, assistant
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    
    # Pre-seed internal products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        seed_products(cursor)
        conn.commit()
        
    # Pre-seed a default report if empty
    cursor.execute("SELECT COUNT(*) FROM reports")
    if cursor.fetchone()[0] == 0:
        seed_report(cursor)
        conn.commit()
        
    conn.close()

def seed_products(cursor):
    products = [
        {
            "name": "Antigravity Chat",
            "description": "Real-time communication and messaging platform designed for secure team collaboration. Focuses on granular workspace configurations, threaded conversations, and native Integrations.",
            "pricing": "Free tier (10k message history limit); Standard ($7.25/user/month) with unlimited search; Enterprise ($15/user/month) with data loss prevention and SSO.",
            "features": json.dumps([
                "Real-time channels and group direct messages with rich formatting",
                "Granular message threads to keep conversations organized and readable",
                "Advanced indexing and search for files, messages, and channels",
                "Native integrations with GitHub, Jira, Figma, and Google Workspace",
                "File sharing up to 1GB per file, with inline previewers for images and PDF",
                "Admin console for custom workspace permissions and audit logging"
            ])
        },
        {
            "name": "Antigravity Docs",
            "description": "Collaborative text editor and internal wiki system. Supports document nesting, interactive block-level edits, and seamless integration with Antigravity Chat.",
            "pricing": "Included in standard Antigravity Suite package; standalone plan for $5/user/month.",
            "features": json.dumps([
                "Real-time co-authoring with multi-cursor tracking and comments",
                "Block-based editing allowing markdown shortcuts, code embeds, and tables",
                "Infinite document hierarchy for structuring product wikis and guidelines",
                "Interactive mentions of team members, chat channels, and tasks",
                "Version control with detailed change tracking and snapshot recovery",
                "Custom document templates for meeting notes, PRDs, and RFCs"
            ])
        },
        {
            "name": "Antigravity Tasks",
            "description": "A flexible project tracking and Kanban board manager for software development and general operations.",
            "pricing": "Included in standard Antigravity Suite package; standalone plan for $6/user/month.",
            "features": json.dumps([
                "Customizable Kanban, list, and calendar views for project tracking",
                "Custom task properties (labels, priority, assignees, estimation points)",
                "Workflow automations (e.g. automatically move task to 'QA' when PR is linked)",
                "Sprint planning boards with burndown charts and velocity tracking",
                "Sub-tasks, checklist management, and dependencies graphing",
                "Unified task inbox aggregating assignments across all active projects"
            ])
        }
    ]
    for p in products:
        cursor.execute(
            "INSERT INTO products (name, description, pricing, features) VALUES (?, ?, ?, ?)",
            (p["name"], p["description"], p["pricing"], p["features"])
        )

def seed_report(cursor):
    swot = {
        "strengths": [
            "Leverages existing user base of Slack to deploy collaborative canvases immediately.",
            "Deeply integrated with Slack messaging, threads, and emoji reactions.",
            "Rich embeds allow interacting with external apps directly within the document."
        ],
        "weaknesses": [
            "Lacks advanced document database features that tools like Notion have.",
            "Export options are currently limited, locking data into the Slack ecosystem."
        ],
        "opportunities": [
            "Encourages Slack users to consolidate wiki documents inside Slack instead of paying for Confluence/Notion.",
            "Positions Slack as a productivity suite rather than just a chat application."
        ],
        "threats": [
            "Directly overlaps with Antigravity Docs, threatening our standalone documents sales to Slack-dependent customers.",
            "Sets a precedent where communication tools absorb collaborative editing workflows."
        ]
    }
    
    gaps = [
        {
            "category": "Collaboration Tools",
            "gap_description": "Our product (Antigravity Docs) operates as a separate workspace tool, whereas Slack Canvas is embedded directly into chat channels, making it much easier to access during discussions.",
            "severity": "High",
            "recommendation": "Build an 'Antigravity Canvas' feature: a lightweight, collaborative notes panel docked directly inside Antigravity Chat channels that syncs with Antigravity Docs."
        },
        {
            "category": "Inter-App Workflows",
            "gap_description": "Slack Canvas allows actionable embedding of workflows (e.g., clicking a button inside Canvas to approve a Jira ticket), whereas Antigravity Docs only supports static links.",
            "severity": "Medium",
            "recommendation": "Extend Antigravity Docs block system to support interactive widget blocks (e.g. Jira issue card with direct status transition dropdown)."
        }
    ]
    
    markdown_content = """# Competitive Intelligence Report: Slack Canvas Launch

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

## 4. Strategic Recommendations

1. **Develop Channel-Level Notes ('Antigravity Canvases'):**
   Introduce a feature in Antigravity Chat that allows pinning a collaborative notes document to any channel. This note should open in a side panel and sync directly with Antigravity Docs, neutralising Slack's core proximity advantage.
   
2. **Double Down on Database Features:**
   Market Antigravity Docs' database capabilities (which Slack Canvas lacks). Focus marketing efforts on 'structured team wikis', 'project registers', and 'knowledge bases' that require relational data modeling.
   
3. **Build Actionable Widgets:**
   Implement interactive card rendering in Antigravity Docs. For example, pasting a task link from Antigravity Tasks should render as an interactive card where the user can assign, close, or estimate the task directly in the document.
"""

    cursor.execute("""
    INSERT INTO reports (competitor_name, feature_name, threat_level, status, swot, gaps, markdown_report, sources)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Slack",
        "Canvas",
        "High",
        "Completed",
        json.dumps(swot),
        json.dumps(gaps),
        markdown_content,
        json.dumps([
            "https://slack.com/blog/news/slack-canvas-now-available-to-all-teams",
            "https://techcrunch.com/2023/05/03/slack-rolls-out-canvases-for-collaborative-documents-in-chats/",
            "https://www.theverge.com/2023/5/3/23709605/slack-canvas-collaborative-notes-features-release-date"
        ])
    ))

# ----------------- DB CRUD HELPERS -----------------

def get_all_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(p) for p in products]

def add_product(name: str, description: str, pricing: str, features: list):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO products (name, description, pricing, features) VALUES (?, ?, ?, ?)",
            (name, description, pricing, json.dumps(features))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_product(product_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = get_db_connection()
    reports = conn.execute("SELECT id, competitor_name, feature_name, threat_level, status, created_at FROM reports ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in reports]

def get_report(report_id: int):
    conn = get_db_connection()
    report = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    if report:
        res = dict(report)
        # Parse JSON fields
        try:
            res["swot"] = json.loads(res["swot"]) if res["swot"] else {}
            res["gaps"] = json.loads(res["gaps"]) if res["gaps"] else []
            res["sources"] = json.loads(res["sources"]) if res["sources"] else []
        except Exception:
            pass
        return res
    return None

def create_empty_report(competitor_name: str, feature_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (competitor_name, feature_name, threat_level, status) VALUES (?, ?, ?, ?)",
        (competitor_name, feature_name, "Low", "Running")
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def update_report_results(report_id: int, threat_level: str, swot: dict, gaps: list, markdown_report: str, sources: list):
    conn = get_db_connection()
    conn.execute("""
    UPDATE reports
    SET threat_level = ?, swot = ?, gaps = ?, markdown_report = ?, sources = ?, status = 'Completed'
    WHERE id = ?
    """, (threat_level, json.dumps(swot), json.dumps(gaps), markdown_report, json.dumps(sources), report_id))
    conn.commit()
    conn.close()

def update_report_status(report_id: int, status: str):
    conn = get_db_connection()
    conn.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
    conn.commit()
    conn.close()

def get_chat_history(report_id: int):
    conn = get_db_connection()
    messages = conn.execute(
        "SELECT sender, message, created_at FROM chat_messages WHERE report_id = ? ORDER BY id ASC",
        (report_id,)
    ).fetchall()
    conn.close()
    return [dict(m) for m in messages]

def add_chat_message(report_id: int, sender: str, message: str):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO chat_messages (report_id, sender, message) VALUES (?, ?, ?)",
        (report_id, sender, message)
    )
    conn.commit()
    conn.close()
