import json
import re
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

class FAQPreprocessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]  # Hierarchical splitting
        )
    
    def clean_text(self, text: str) -> str:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace while preserving paragraph breaks
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def process_faq_data(self, input_file: str) -> List[Dict]:
        processed_chunks = []
        
        with open(input_file, 'r') as f:
            articles = json.load(f)
            
        for article in articles:
            # Extract article metadata
            metadata = {
                'title': article.get('article_title', ''),
                'url': article.get('article_url', ''),
                'collection': article.get('collection_title', '')
            }
            
            # Combine structured content into a single coherent text
            content_parts = []
            for item in article.get('structured_content', []):
                if item.get('type') == 'paragraph':
                    content_parts.append(item.get('content', ''))
            
            full_text = ' '.join(content_parts)
            clean_content = self.clean_text(full_text)
            
            # Split into chunks while preserving context
            chunks = self.text_splitter.split_text(clean_content)
            
            # Add each chunk with its metadata
            for chunk in chunks:
                processed_chunks.append({
                    'text': chunk,
                    'metadata': metadata
                })
            
            # Add related articles as separate chunks for context
            for related in article.get('related_articles', []):
                processed_chunks.append({
                    'text': f"Related article: {related.get('title')} - For more information visit: {related.get('url')}",
                    'metadata': {
                        **metadata,
                        'type': 'related_article',
                        'related_title': related.get('title'),
                        'related_url': related.get('url')
                    }
                })
        
        return processed_chunks

# Usage example:
if __name__ == "__main__":
    processor = FAQPreprocessor()
    processed_data = processor.process_faq_data('../data/highrise_faq.json')
    
    # Save processed chunks
    with open('../data/processed_chunks.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
