# Use a base Python image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies required for building many Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libatlas-base-dev \
    gcc \
    g++ && \
    rm -rf /var/lib/apt/lists/*

# Install core Python build tools *before* main requirements
RUN pip install --no-cache-dir setuptools wheel

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (punkt, stopwords, wordnet)
RUN python -c "import nltk; nltk.download('punkt', download_dir='/usr/local/share/nltk_data'); nltk.download('stopwords', download_dir='/usr/local/share/nltk_data'); nltk.download('wordnet', download_dir='/usr/local/share/nltk_data')"
ENV NLTK_DATA=/usr/local/share/nltk_data

# Copy all other project files (including main.py, input JSONs, PDFs) into the container
COPY . .

# EXPLICITLY SET ENTRYPOINT
# This ensures that 'python main.py' is *always* the executable part of the command.
# Any arguments provided to 'docker run' will be appended to this ENTRYPOINT.
ENTRYPOINT ["python", "main.py"]

# Set the default CMD, which provides default arguments to the ENTRYPOINT.
# These defaults will be used if 'docker run' is executed without any further arguments.
CMD ["sample_input.json", "output.json"]