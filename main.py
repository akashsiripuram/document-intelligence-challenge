#!/usr/bin/env python3
"""
Persona-Driven Document Intelligence System
Challenge 1B: Connect What Matters — For the User Who Matters
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple
import re
import logging
from pathlib import Path

# PDF processing
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    def __init__(self):
        """Initialize the document intelligence system."""
        self.setup_nltk()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def setup_nltk(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF with page numbers and section detection."""
        try:
            doc = fitz.open(pdf_path)
            pages_content = {}
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages_content[page_num + 1] = {
                    'text': text,
                    'sections': self.detect_sections(text)
                }
            
            doc.close()
            return pages_content
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return {}

    def detect_sections(self, text: str) -> List[Dict[str, Any]]:
        """Detect sections in text using patterns and formatting."""
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        # Patterns for section headers
        header_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^\d+\.\s+[A-Z]',    # Numbered sections
            r'^[A-Z][a-z]+\s[A-Z][a-z]+',  # Title Case
            r'^[A-Z][a-z\s]+:',   # Colon endings
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            for pattern in header_patterns:
                if re.match(pattern, line) and len(line) < 100:
                    is_header = True
                    break
            
            if is_header:
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                
                # Start new section
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        # If no sections detected, create one main section
        if not sections and text.strip():
            sections.append({
                'title': "Main Content",
                'content': text.strip()
            })
        
        return sections

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Tokenize and remove stopwords
        words = word_tokenize(text)
        words = [self.lemmatizer.lemmatize(word) for word in words 
                if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(words)

    def create_persona_profile(self, persona: Dict[str, str], job: Dict[str, str]) -> Dict[str, Any]:
        """Create a comprehensive persona profile with keywords and priorities."""
        role = persona.get('role', '').lower()
        task = job.get('task', '').lower()
        
        # Define role-specific keywords and priorities
        role_keywords = {
            'travel planner': [
                'itinerary', 'accommodation', 'restaurant', 'attraction', 'activity', 
                'transportation', 'hotel', 'booking', 'schedule', 'location', 'sightseeing',
                'tour', 'experience', 'dining', 'nightlife', 'beach', 'cultural', 'budget',
                'group', 'friend', 'vacation', 'trip', 'destination'
            ],
            'researcher': [
                'methodology', 'analysis', 'data', 'study', 'research', 'experiment',
                'result', 'conclusion', 'literature', 'reference', 'evaluation'
            ],
            'student': [
                'concept', 'theory', 'example', 'definition', 'explanation', 'key',
                'important', 'exam', 'study', 'learn', 'understand'
            ],
            'analyst': [
                'trend', 'performance', 'metric', 'analysis', 'comparison', 'data',
                'insight', 'strategy', 'market', 'financial', 'revenue'
            ]
        }
        
        # Extract keywords based on role and task
        keywords = []
        for role_type, role_words in role_keywords.items():
            if role_type in role:
                keywords.extend(role_words)
        
        # Add task-specific keywords
        task_words = word_tokenize(task)
        task_words = [word for word in task_words if word not in self.stop_words]
        keywords.extend(task_words)
        
        # Remove duplicates and create weighted keywords
        unique_keywords = list(set(keywords))
        
        return {
            'role': role,
            'task': task,
            'keywords': unique_keywords,
            'primary_focus': self.extract_primary_focus(task),
            'secondary_focus': self.extract_secondary_focus(role, task)
        }

    def extract_primary_focus(self, task: str) -> List[str]:
        """Extract primary focus areas from the task."""
        focus_patterns = {
            'planning': ['plan', 'organize', 'schedule', 'arrange'],
            'analysis': ['analyze', 'evaluate', 'assess', 'compare'],
            'learning': ['learn', 'study', 'understand', 'prepare'],
            'research': ['research', 'investigate', 'explore', 'review']
        }
        
        primary = []
        for focus, patterns in focus_patterns.items():
            if any(pattern in task.lower() for pattern in patterns):
                primary.append(focus)
        
        return primary if primary else ['general']

    def extract_secondary_focus(self, role: str, task: str) -> List[str]:
        """Extract secondary focus areas."""
        combined_text = f"{role} {task}".lower()
        
        secondary_patterns = {
            'group_activities': ['group', 'friends', 'team', 'colleagues'],
            'budget_conscious': ['budget', 'affordable', 'cheap', 'cost'],
            'time_sensitive': ['days', 'quick', 'short', 'brief'],
            'experience_focused': ['experience', 'memorable', 'special', 'unique']
        }
        
        secondary = []
        for focus, patterns in secondary_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                secondary.append(focus)
        
        return secondary

    def calculate_relevance_score(self, section_content: str, persona_profile: Dict[str, Any]) -> float:
        """Calculate relevance score for a section based on persona profile."""
        processed_content = self.preprocess_text(section_content)
        
        if not processed_content.strip():
            return 0.0
        
        # Keyword matching score
        keyword_score = 0.0
        content_words = set(processed_content.split())
        
        for keyword in persona_profile['keywords']:
            if keyword.lower() in content_words:
                keyword_score += 1.0
        
        # Normalize keyword score
        keyword_score = keyword_score / len(persona_profile['keywords']) if persona_profile['keywords'] else 0.0
        
        # Primary focus score
        primary_score = 0.0
        for focus in persona_profile['primary_focus']:
            if focus in processed_content:
                primary_score += 2.0
        
        # Secondary focus score
        secondary_score = 0.0
        for focus in persona_profile['secondary_focus']:
            if focus in processed_content:
                secondary_score += 1.0
        
        # Content length penalty (prefer substantial content)
        length_score = min(len(processed_content.split()) / 50.0, 1.0)
        
        # Combine scores with weights
        total_score = (
            keyword_score * 0.4 +
            primary_score * 0.3 +
            secondary_score * 0.2 +
            length_score * 0.1
        )
        
        return total_score

    def extract_and_rank_sections(self, documents_content: Dict[str, Dict], persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and rank sections from all documents."""
        all_sections = []
        
        for doc_name, pages in documents_content.items():
            for page_num, page_content in pages.items():
                for section in page_content['sections']:
                    if section['content'].strip():
                        relevance_score = self.calculate_relevance_score(
                            section['content'], persona_profile
                        )
                        
                        all_sections.append({
                            'document': doc_name,
                            'page_number': page_num,
                            'section_title': section['title'],
                            'content': section['content'],
                            'relevance_score': relevance_score
                        })
        
        # Sort by relevance score (descending)
        all_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Add importance rank
        for i, section in enumerate(all_sections[:10]):  # Top 10 sections
            section['importance_rank'] = i + 1
        
        return all_sections[:5]  # Return top 5 sections

    def refine_subsections(self, sections: List[Dict[str, Any]], persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create refined subsections with improved content."""
        refined_subsections = []
        
        for section in sections:
            content = section['content']
            
            # Split content into sentences
            sentences = sent_tokenize(content)
            
            # Score each sentence
            sentence_scores = []
            for sentence in sentences:
                score = self.calculate_relevance_score(sentence, persona_profile)
                sentence_scores.append((sentence, score))
            
            # Sort sentences by score and take top ones
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            top_sentences = [s[0] for s in sentence_scores[:5]]  # Top 5 sentences
            
            # Create refined text
            refined_text = ' '.join(top_sentences)
            
            # Ensure minimum length
            if len(refined_text) < 100 and len(sentences) > 5:
                refined_text = ' '.join(sentences[:3])  # Take first 3 sentences if refined is too short
            
            refined_subsections.append({
                'document': section['document'],
                'page_number': section['page_number'],
                'refined_text': refined_text.strip()
            })
        
        return refined_subsections

    def process_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function."""
        start_time = time.time()
        
        # Extract input data
        documents = input_data['documents']
        persona = input_data['persona']
        job = input_data['job_to_be_done']
        
        # Create persona profile
        persona_profile = self.create_persona_profile(persona, job)
        
        # Extract text from all documents
        documents_content = {}
        for doc in documents:
            filename = doc['filename']
            if os.path.exists(filename):
                logger.info(f"Processing {filename}")
                documents_content[filename] = self.extract_text_from_pdf(filename)
            else:
                logger.warning(f"File not found: {filename}")
        
        # Extract and rank sections
        top_sections = self.extract_and_rank_sections(documents_content, persona_profile)
        
        # Create refined subsections
        refined_subsections = self.refine_subsections(top_sections, persona_profile)
        
        # Prepare output
        output = {
            "metadata": {
                "input_documents": [doc['filename'] for doc in documents],
                "persona": persona['role'],
                "job_to_be_done": job['task'],
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section['document'],
                    "section_title": section['section_title'],
                    "importance_rank": section['importance_rank'],
                    "page_number": section['page_number']
                }
                for section in top_sections
            ],
            "subsection_analysis": refined_subsections
        }
        
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        return output

def main():
    """Main function to run the document intelligence system."""
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_json_file> <output_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load input data
    try:
        with open(input_file, 'r') as f:
            input_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading input file: {str(e)}")
        sys.exit(1)
    
    # Initialize and run system
    system = DocumentIntelligenceSystem()
    result = system.process_documents(input_data)
    
    # Save output
    try:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
        logger.info(f"Output saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving output file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()