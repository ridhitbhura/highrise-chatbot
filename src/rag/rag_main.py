import os
import json
from dotenv import load_dotenv
from ..common.preprocessing.text_processor import FAQPreprocessor
from ..common.embeddings.pinecone_loader import PineconeLoader
from .rag_chatbot import RAGChatbot

def initialize_system():
    """Initialize and load embeddings (run this once)"""
    load_dotenv()
    
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENV = os.getenv('PINECONE_ENVIRONMENT')
    INDEX_NAME = 'highrise-faq'
    
    print("Processing FAQ data...")
    processor = FAQPreprocessor()
    processed_data = processor.process_faq_data('data/highrise_faq.json')
    
    print("Loading embeddings to Pinecone...")
    loader = PineconeLoader(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENV,
        index_name=INDEX_NAME,
    )
    
    # Process in smaller batches
    batch_size = 20
    for i in range(0, len(processed_data), batch_size):
        batch = processed_data[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} of {len(processed_data)//batch_size + 1}...")
        loader.upsert_vectors(batch)

    print("\nFinished loading all embeddings!")

def chat_loop():
    """Interactive chat loop"""
    load_dotenv()
    INDEX_NAME = 'highrise-faq'
    
    # Add this line to get OpenAI API key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    print("Initializing chatbot...")
    chatbot = RAGChatbot(INDEX_NAME, 'faq')
    
    print("\nChatbot ready! Type 'quit' to exit.")
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        answer = chatbot.ask(question)
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--initialize":
        initialize_system()
    else:
        chat_loop() 