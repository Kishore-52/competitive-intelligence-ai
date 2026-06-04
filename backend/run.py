import uvicorn
import os

if __name__ == "__main__":
    # Ensure we are in the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting Multi-Agent Competitive Intelligence Backend Server...")
    print("API will be available at http://127.0.0.1:8000")
    print("API docs will be available at http://127.0.0.1:8000/docs")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
