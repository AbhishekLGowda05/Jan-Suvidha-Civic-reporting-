# manager/debugDB.py
import sys
import os

# Add the current directory (manager) and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

# Now import from the tools directory
from tools.tools import debug_database_status

if __name__ == "__main__":
    print("=== Database Debug Information ===")
    debug_database_status()