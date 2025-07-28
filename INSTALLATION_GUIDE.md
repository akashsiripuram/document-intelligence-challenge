# Complete Installation and Usage Guide

## System Requirements
- Python 3.9 or higher
- Docker (optional, but recommended)
- 4GB RAM minimum
- CPU-only system (no GPU required)

## Method 1: Direct Python Installation

### Step 1: Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv gcc g++
```

#### On macOS:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python gcc
```

#### On Windows:
1. Download Python 3.9+ from https://python.org
2. Install Visual Studio Build Tools or Visual Studio Community
3. Open Command Prompt as Administrator

### Step 2: Create Project Directory
```bash
mkdir document-intelligence-system
cd document-intelligence-system
```

### Step 3: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 4: Install Python Dependencies
```bash
pip install --upgrade pip
pip install PyMuPDF==1.23.14 nltk==3.8.1 numpy==1.24.3 scikit-learn==1.3.2
```

### Step 5: Download NLTK Data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### Step 6: Copy Project Files
Copy these files to your project directory:
- `main.py`
- `requirements.txt`
- `sample_input.json`
- `approach_explanation.md`

### Step 7: Prepare Your Documents
Place your PDF documents in the same directory as `main.py`

### Step 8: Run the System
```bash
python main.py sample_input.json output.json
```

## Method 2: Docker Installation (Recommended)

### Step 1: Install Docker
#### On Ubuntu:
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and log back in
```

#### On macOS:
Download and install Docker Desktop from https://docker.com

#### On Windows:
Download and install Docker Desktop from https://docker.com

### Step 2: Create Project Directory
```bash
mkdir document-intelligence-system
cd document-intelligence-system
```

### Step 3: Copy Project Files
Copy these files to your project directory:
- `main.py`
- `requirements.txt`
- `Dockerfile`
- `sample_input.json`
- `approach_explanation.md`

### Step 4: Place PDF Documents
Copy your PDF documents to the project directory

### Step 5: Build Docker Image
```bash
docker build -t doc-intelligence .
```

### Step 6: Run with Docker
```bash
docker run -v $(pwd):/app doc-intelligence input.json output.json
```

## Usage Instructions

### Input File Format
Create a JSON file with this structure:
```json
{
    "challenge_info": {
        "challenge_id": "your_challenge_id",
        "test_case_name": "your_test_case",
        "description": "Description"
    },
    "documents": [
        {
            "filename": "document1.pdf",
            "title": "Document 1 Title"
        }
    ],
    "persona": {
        "role": "Your Role (e.g., Travel Planner, Researcher, Student)"
    },
    "job_to_be_done": {
        "task": "Your specific task description"
    }
}
```

### Command Line Usage
```bash
# Basic usage
python main.py input.json output.json

# With Docker
docker run -v $(pwd):/app doc-intelligence input.json output.json
```

### Output Format
The system generates a JSON file with:
- Metadata (input documents, persona, job, timestamp)
- Extracted sections (ranked by importance)
- Subsection analysis (refined content)

## Testing the Installation

### Step 1: Create Test Input
Use the provided `sample_input.json` or create your own

### Step 2: Add Sample PDFs
Place some PDF documents in your directory

### Step 3: Run Test
```bash
python main.py sample_input.json test_output.json
```

### Step 4: Verify Output
Check that `test_output.json` is created with the expected structure

## Troubleshooting

### Common Issues and Solutions

#### "Module not found" errors:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

#### NLTK download errors:
```bash
python -c "import nltk; nltk.download('all')"
```

#### PDF processing errors:
- Ensure PDF files are not corrupted
- Check file permissions
- Verify file paths in input JSON

#### Docker build errors:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild image
docker build --no-cache -t doc-intelligence .
```

#### Memory issues:
- Reduce number of documents processed simultaneously
- Use smaller PDF files for testing
- Increase system RAM if possible

### Performance Tips
1. Process fewer documents per batch for faster execution
2. Use SSD storage for better I/O performance
3. Close other applications to free up RAM
4. Use Docker for consistent performance across systems

## Validation

### Expected Performance
- Processing time: < 60 seconds for 3-5 documents
- Memory usage: < 2GB RAM
- Model size: < 1GB total

### Output Validation
1. Check that all required fields are present in output JSON
2. Verify importance rankings are 1-5
3. Ensure page numbers are correct
4. Confirm section titles match document content

## Support
For issues or questions:
1. Check the troubleshooting section above
2. Verify your system meets all requirements
3. Test with smaller document sets first
4. Review the approach_explanation.md for methodology details