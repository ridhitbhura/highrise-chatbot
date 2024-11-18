import os
from typing import List, Dict
import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document

class PineconeLoader:
    def __init__(self, api_key: str, environment: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.embeddings = OpenAIEmbeddings(
            model='text-embedding-ada-002',
            openai_api_key=os.environ.get('OPENAI_API_KEY')
        )
        self.create_index()

    
    def create_index(self) -> None:
        """Create Pinecone index if it doesn't exist"""
        if self.index_name not in self.pc.list_indexes().names():
            dimension = 1536
            
            spec = ServerlessSpec(
                cloud=os.environ.get('PINECONE_CLOUD', 'aws'),
                region=os.environ.get('PINECONE_REGION', 'us-east-1')
            )
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=spec
            )

    def upsert_vectors(self, chunks: List[Dict]) -> None:
        """Upsert vectors to Pinecone index with metadata"""
        index = self.pc.Index(self.index_name)
        vectors = []
        
        for i, chunk in enumerate(chunks):
            # Check if chunk is a tuple and unpack accordingly
            if isinstance(chunk, tuple):
                text = chunk[0]  # Assuming text is the first element
                metadata = chunk[1]  # Assuming metadata is the second element
            else:
                text = chunk['text']
                metadata = chunk.get('metadata', {})  # Use get() with default empty dict
                
                # Handle case where metadata might be a list
                if isinstance(metadata, list):
                    metadata = metadata[0] if metadata else {}  # Take first item if list is not empty, else empty dict
            
            # Ensure metadata is a dictionary before using get()
            if not isinstance(metadata, dict):
                metadata = {}
            
            embedding = self.generate_embedding(text)
            vectors.append((
                f"chunk_{i}",  # Unique ID for each chunk
                embedding,
                {
                    'text': text,
                    'title': metadata.get('title', ''),  # Use get() with default values
                    'url': metadata.get('url', ''),
                    'collection': metadata.get('collection', '')
                }
            ))
        
        index.upsert(vectors=vectors)

    def generate_embedding(self, text):
        """Generate embeddings for the given text using OpenAI."""
        return self.embeddings.embed_query(text)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Query the index and return relevant chunks with metadata"""
        index = self.pc.Index(self.index_name)
        query_embedding = self.generate_embedding(query_text)
        
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return [
            {
                'text': match.metadata['text'],
                'title': match.metadata['title'],
                'url': match.metadata['url'],
                'score': match.score
            }
            for match in results.matches
        ]

# Usage example:
if __name__ == "__main__":
    # Load processed chunks
    with open('../data/processed_chunks.json', 'r') as f:
        chunks = json.load(f)
    
    # Initialize loader and create index
    loader = PineconeLoader(api_key=os.environ.get("PINECONE_API_KEY"), environment=os.environ.get("PINECONE_ENVIRONMENT"), index_name='highrise-faq')
    
    # Load chunks into Pinecone
    loader.upsert_vectors(chunks) 