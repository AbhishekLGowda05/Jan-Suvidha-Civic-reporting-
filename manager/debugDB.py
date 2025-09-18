# debug_database.py
import sys
import os

# Add the tools directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'manager'))
from tools.tools import debug_database_status

if __name__ == "__main__":
    print("=== Database Debug Information ===")
    debug_database_status()