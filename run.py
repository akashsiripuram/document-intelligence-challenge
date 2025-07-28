#!/usr/bin/env python3
"""
Runner script for Document Intelligence System
Handles setup, validation, and execution
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['fitz', 'nltk', 'numpy', 'sklearn']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'fitz':
                import fitz
            elif package == 'nltk':
                import nltk
            elif package == 'numpy':
                import numpy
            elif package == 'sklearn':
                import sklearn
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_nltk():
    """Download required NLTK data."""
    print("\n📚 Setting up NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error setting up NLTK: {e}")
        return False

def validate_input_file(input_file):
    """Validate input JSON file."""
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ['documents', 'persona', 'job_to_be_done']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field in input: {field}")
                return False
        
        # Check documents exist
        missing_docs = []
        for doc in data['documents']:
            if not os.path.exists(doc['filename']):
                missing_docs.append(doc['filename'])
        
        if missing_docs:
            print(f"❌ Missing document files: {missing_docs}")
            return False
        
        print(f"✅ Input file validated: {len(data['documents'])} documents found")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in input file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating input file: {e}")
        return False

def run_system(input_file, output_file):
    """Run the document intelligence system."""
    print(f"\n🚀 Running document intelligence system...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    start_time = time.time()
    
    try:
        # Import and run the main system
        from main import DocumentIntelligenceSystem
        
        # Load input data
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        
        # Initialize and process
        system = DocumentIntelligenceSystem()
        result = system.process_documents(input_data)
        
        # Save output
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
        
        processing_time = time.time() - start_time
        print(f"✅ Processing completed successfully in {processing_time:.2f} seconds")
        print(f"✅ Output saved to: {output_file}")
        
        # Display summary
        print(f"\n📊 Summary:")
        print(f"   - Documents processed: {len(result['metadata']['input_documents'])}")
        print(f"   - Sections extracted: {len(result['extracted_sections'])}")
        print(f"   - Subsections analyzed: {len(result['subsection_analysis'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running system: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_files():
    """Create sample files for testing."""
    print("\n📝 Creating sample files...")
    
    # Create sample input if it doesn't exist
    if not os.path.exists('sample_input.json'):
        sample_input = {
            "challenge_info": {
                "challenge_id": "test_001",
                "test_case_name": "sample_test",
                "description": "Sample test case"
            },
            "documents": [
                {
                    "filename": "sample_document.pdf",
                    "title": "Sample Document"
                }
            ],
            "persona": {
                "role": "Researcher"
            },
            "job_to_be_done": {
                "task": "Analyze the document content for key insights."
            }
        }
        
        with open('sample_input.json', 'w') as f:
            json.dump(sample_input, f, indent=4)
        print("✅ Created sample_input.json")
    
    return True

def main():
    """Main function to set up and run the system."""
    print("🔧 Document Intelligence System Setup & Runner")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python run.py setup                    # Set up the system")
        print("  python run.py run <input> <output>     # Run the system")
        print("  python run.py test                     # Run with sample data")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        print("\n🔧 Setting up system...")
        
        # Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Check and install dependencies
        missing = check_dependencies()
        if missing:
            print(f"\n📦 Missing packages: {missing}")
            if input("Install missing packages? (y/N): ").lower().startswith('y'):
                if not install_dependencies():
                    sys.exit(1)
                # Recheck dependencies
                missing = check_dependencies()
                if missing:
                    print(f"❌ Still missing packages: {missing}")
                    sys.exit(1)
            else:
                print("❌ Cannot proceed without required packages")
                sys.exit(1)
        
        # Setup NLTK
        if not setup_nltk():
            sys.exit(1)
        
        # Create sample files
        create_sample_files()
        
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("  1. Place your PDF documents in this directory")
        print("  2. Create or modify input.json with your requirements")
        print("  3. Run: python run.py run input.json output.json")
        
    elif command == 'run':
        if len(sys.argv) != 4:
            print("Usage: python run.py run <input_file> <output_file>")
            sys.exit(1)
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        print("\n🔍 Pre-flight checks...")
        
        # Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Check dependencies
        missing = check_dependencies()
        if missing:
            print(f"❌ Missing packages: {missing}")
            print("Run 'python run.py setup' first")
            sys.exit(1)
        
        # Validate input
        if not validate_input_file(input_file):
            sys.exit(1)
        
        # Run system
        if not run_system(input_file, output_file):
            sys.exit(1)
    
    elif command == 'test':
        print("\n🧪 Running test with sample data...")
        
        # Check if sample files exist
        if not os.path.exists('sample_input.json'):
            create_sample_files()
        
        # Run with sample data
        if run_system('sample_input.json', 'test_output.json'):
            print("\n✅ Test completed successfully!")
            print("Check test_output.json for results")
        else:
            print("❌ Test failed")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: setup, run, test")
        sys.exit(1)

if __name__ == "__main__":
    main()