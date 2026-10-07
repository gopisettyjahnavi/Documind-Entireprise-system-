"""
Quick Start Script for DocuMind Enterprise

This script helps set up and run the project quickly.
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python 3.10+ required. Current: {version.major}.{version.minor}")
        return False


def check_ollama():
    """Check if Ollama is installed and running"""
    print("Checking Ollama installation...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            if "llama2" in result.stdout:
                print("✅ llama2 model is available")
                return True
            else:
                print("⚠️  llama2 model not found")
                print("   Run: ollama pull llama2")
                return False
        else:
            print("❌ Ollama not responding")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("   Download from: https://ollama.ai/")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("Checking environment configuration...")
    if Path(".env").exists():
        print("✅ .env file exists")
        return True
    elif Path(".env.example").exists():
        print("⚠️  .env file not found")
        print("   Creating .env from .env.example...")
        try:
            with open(".env.example", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("✅ .env file created")
            return True
        except Exception as e:
            print(f"❌ Error creating .env: {e}")
            return False
    else:
        print("❌ .env.example not found")
        return False


def check_dependencies():
    """Check if dependencies are installed"""
    print("Checking dependencies...")
    try:
        import fastapi
        import chromadb
        import ollama
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"⚠️  Missing dependencies: {e}")
        print("   Run: pip install -r requirements.txt")
        return False


def check_chroma_db():
    """Check if ChromaDB has data"""
    print("Checking vector database...")
    try:
        import chromadb
        client = chromadb.PersistentClient(path="chroma_db")
        collection = client.get_collection(name="documind")
        count = collection.count()
        print(f"✅ ChromaDB ready with {count} embeddings")
        return True
    except Exception as e:
        print(f"⚠️  ChromaDB not initialized: {e}")
        print("   Run ingestion first: python ingestion/ingest.py")
        return False


def start_server():
    """Start the FastAPI server"""
    print("\nStarting FastAPI server...")
    print("Press Ctrl+C to stop\n")
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")


def main():
    """Main setup flow"""
    print_header("DocuMind Enterprise - Quick Start")
    
    # Pre-flight checks
    checks = [
        ("Python Version", check_python_version),
        ("Ollama", check_ollama),
        ("Environment Config", check_env_file),
        ("Dependencies", check_dependencies),
        ("Vector Database", check_chroma_db),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
        print()
    
    if not all_passed:
        print_header("Setup Incomplete")
        print("❌ Some checks failed. Please resolve the issues above.\n")
        print("Setup Steps:")
        print("  1. Install Ollama: https://ollama.ai/")
        print("  2. Pull model: ollama pull llama2")
        print("  3. Install deps: pip install -r requirements.txt")
        print("  4. Ingest docs: python ingestion/ingest.py")
        print("\nThen run this script again.")
        return 1
    
    print_header("All Checks Passed!")
    print("Ready to start the server\n")
    
    response = input("Start the server now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        start_server()
    else:
        print("\n✅ Setup complete!")
        print("\nTo start manually:")
        print("  python -m uvicorn backend.app:app --reload")
        print("\nTo run demo:")
        print("  python demo.py")
        print("\nAPI docs will be at: http://localhost:8000/docs")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
