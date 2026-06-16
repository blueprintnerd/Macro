import uvicorn
import os
import sys
from background.api import app
from background.sqlite import setup_database

def main():
    print("Macro Backend Starting...")
    # Ensure database is initialized and migrated from any legacy config.json
    setup_database()
    
    print("\n-------------------------------------------------------")
    print("To configure Macro, run: streamlit run server/web_setup.py")
    print("To use the client, run: streamlit run client/web_client.py")
    print("-------------------------------------------------------\n")
    
    uvicorn.run(app, host="0.0.0.0", port=1470)

if __name__ == "__main__":
    main()
