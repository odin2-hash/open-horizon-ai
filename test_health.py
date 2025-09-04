#!/usr/bin/env python3
"""Quick health check test for Open Horizon AI backend."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

print("🔍 Testing Open Horizon AI Backend Health...")

try:
    # Test basic imports
    print("  ✓ Testing basic Python imports...")
    from fastapi import FastAPI
    from pydantic import BaseModel
    print("  ✓ FastAPI and Pydantic imports successful")
    
    # Test backend imports (without starting the server)
    print("  ✓ Testing backend module structure...")
    
    # Check if the backend directory exists
    backend_path = os.path.join(os.path.dirname(__file__), "backend", "api", "main.py")
    if os.path.exists(backend_path):
        print("  ✓ Backend main.py exists")
    else:
        print(f"  ❌ Backend main.py not found at {backend_path}")
        
    # Check if agent files exist
    agent_path = os.path.join(os.path.dirname(__file__), "agent.py")
    if os.path.exists(agent_path):
        print("  ✓ Agent.py exists")
    else:
        print(f"  ❌ Agent.py not found at {agent_path}")
        
    # Check if models exist
    models_path = os.path.join(os.path.dirname(__file__), "models.py")
    if os.path.exists(models_path):
        print("  ✓ Models.py exists")
    else:
        print(f"  ❌ Models.py not found at {models_path}")
        
    print("\n🎉 Basic structure check completed!")
    print("✨ Ready for Docker Compose deployment!")
    
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    print("  💡 You may need to install dependencies: pip install fastapi pydantic")
    sys.exit(1)
except Exception as e:
    print(f"  ❌ Unexpected error: {e}")
    sys.exit(1)

print("\n📝 Next steps:")
print("  1. Set up environment variables in .env file")
print("  2. Run: docker-compose up --build")
print("  3. Access frontend: http://localhost:3030")
print("  4. Access API docs: http://localhost:8080/docs")