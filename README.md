# Competitive Intelligence AI

A multi-agent competitive intelligence platform built to help product teams track competitor activity, collect market data, and generate actionable reports.

## Project Overview

- **Backend:** Python API served with FastAPI and Uvicorn.
- **Frontend:** React + Vite dashboard experience.
- **Purpose:** Automate competitor analysis, enable rapid research, and generate unbiased intelligence for product strategy.

## Repository Structure

- `backend/` - Python API, data model, vector store, and agent orchestration logic.
- `frontend/` - Vite-powered React UI for dashboards and reports.
- `run_all.py` - Top-level script for orchestrating the application from the repository root.

## Setup

### Backend

1. Create a Python environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Start the backend server:
   ```bash
   python backend/run.py
   ```

### Frontend

1. Change into the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Notes

- The backend API is available at `http://127.0.0.1:8000`.
- API docs are available at `http://127.0.0.1:8000/docs`.
- The frontend runs on Vite and connects to the backend API.

## License

This repository is maintained by the project owner.
