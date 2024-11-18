import json
import os
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from thefuzz import fuzz
import re
import time

class SimpleFAQChatbot:
    def __init__(self, faq_file: str):
        load_dotenv()
        
        # Setup logging
        self._setup_logging()
        
        # Load FAQ data
        self.faq_data = self._load_faq_data(faq_file)
        
        # Initialize OpenAI
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.environ.get('OPENAI_API_KEY')
        )
        
        self.llm = ChatOpenAI(
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            model_name='gpt-4',
            temperature=0.1
        )
        
        # Track conversation state
        self.conversation_history = []
        self.unanswered_questions = []
        
        # Process FAQ data
        self.processed_faqs = self._process_faq_data()
        # Cache embeddings
        self.question_embeddings = self._cache_embeddings()
        
        # Add synonym mappings
        self.synonyms = {
            'coins': 'gold',
            'credits': 'gold',
            'money': 'gold',
            'currency': 'gold',
            'character': 'avatar',
            'profile': 'avatar',
            'person': 'avatar',
            'report': ['report player', 'reporting'],
            'block': ['blocking', 'ban'],
            'customize': ['customise', 'change', 'modify'],
        }
        
        # Add common typo patterns
        self.typo_patterns = {
            r'avatr|avtar|avatr': 'avatar',
            r'customi[sz]e?': 'customize',
            r'g[ou]ld': 'gold',
            r'reportin?g?': 'report',
            r'block(ing)?': 'block',
        }
        
        self.session_data = {}
    
    def _setup_logging(self):
        """Configure logging settings"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'chatbot_{timestamp}.log'),
                logging.StreamHandler()
            ]
        )
    
    def _load_faq_data(self, faq_file: str) -> Dict:
        """Load and validate FAQ data"""
        try:
            with open(faq_file, 'r') as f:
                data = json.load(f)
            logging.info(f"Successfully loaded FAQ data from {faq_file}")
            return data
        except Exception as e:
            logging.error(f"Error loading FAQ data: {str(e)}")
            raise
    
    def _process_faq_data(self) -> List[Dict]:
        """Process FAQ data into a simple format"""
        processed = []
        for article in self.faq_data:
            # Extract main content
            content = ' '.join([
                item['content'] 
                for item in article.get('structured_content', [])
                if item.get('type') == 'paragraph'
            ])
            
            processed.append({
                'title': article.get('article_title', ''),
                'content': content,
                'url': article.get('article_url', '')
            })
        return processed
    
    def _cache_embeddings(self) -> List[np.ndarray]:
        """Cache embeddings for all FAQ titles"""
        return [
            self.embeddings.embed_query(faq['title'])
            for faq in self.processed_faqs
        ]
    
    def _find_most_similar(self, query: str, top_k: int = 3) -> List[Tuple[int, float]]:
        """Find most similar FAQs using embeddings"""
        query_embedding = self.embeddings.embed_query(query)
        
        # Calculate similarities
        similarities = [
            (i, np.dot(query_embedding, faq_embedding))
            for i, faq_embedding in enumerate(self.question_embeddings)
        ]
        
        # Sort by similarity
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    def _preprocess_question(self, question: str) -> str:
        """Preprocess question to handle typos and synonyms"""
        # Convert to lowercase
        processed = question.lower()
        
        # Fix common typos using patterns
        for pattern, correction in self.typo_patterns.items():
            processed = re.sub(pattern, correction, processed)
        
        # Replace synonyms
        for synonym, main_term in self.synonyms.items():
            if isinstance(main_term, list):
                for term in main_term:
                    processed = processed.replace(synonym, term)
            else:
                processed = processed.replace(synonym, main_term)
        
        return processed
    
    def _is_multi_part_question(self, question: str) -> bool:
        """Check if question contains multiple parts"""
        conjunctions = ['and', 'or', 'also', 'plus']
        question_marks = question.count('?')
        
        return any(conj in question.lower() for conj in conjunctions) or question_marks > 1
    
    def _split_multi_part_question(self, question: str) -> List[str]:
        """Split multi-part question into individual questions"""
        # Split by question marks
        parts = [q.strip() + '?' for q in question.split('?') if q.strip()]
        
        # If no question marks found, split by conjunctions
        if len(parts) <= 1:
            for conj in ['and', 'or', 'also', 'plus']:
                if conj in question.lower():
                    parts = [p.strip() for p in question.split(conj) if p.strip()]
        
        return parts
    
    def _needs_clarification(self, question: str) -> Optional[str]:
        """Check if question needs clarification and return clarifying question"""
        # Common patterns that need context
        vague_patterns = {
            r'how (much|many)': 'Could you specify what you\'re asking about?',
            r'when (is|will)': 'Which feature or event are you asking about?',
            r'(how|where) (do|can) (i|we) get': 'What specifically are you looking to get?',
            r'what is it': 'Could you specify what you\'re referring to?',
            r'how does it work': 'Which feature are you asking about?'
        }
        
        question = question.lower()
        for pattern, clarification in vague_patterns.items():
            if re.search(pattern, question):
                return clarification
        
        return None
    
    def ask(self, question: str) -> str:
        """Enhanced answer generation with better handling of edge cases"""
        logging.info(f"Received question: {question}")
        
        # Handle basic cases (greetings, goodbyes, empty questions)
        if self._is_greeting(question):
            return "Hello! I'm the Highrise FAQ chatbot. How can I help you today?"
        
        if self._is_goodbye(question):
            return "Goodbye! Feel free to come back if you have more questions about Highrise!"
        
        if not question or len(question.strip()) < 3:
            return "Could you please ask a complete question? I'm here to help with any Highrise-related queries!"
        
        # Check if question needs clarification
        clarification = self._needs_clarification(question)
        if clarification:
            return f"{clarification} This will help me provide a more accurate answer."
        
        # Handle multi-part questions
        if self._is_multi_part_question(question):
            parts = self._split_multi_part_question(question)
            responses = []
            
            for part in parts:
                processed_part = self._preprocess_question(part)
                response = self._generate_response(processed_part)
                responses.append(response)
            
            return "\n\n".join(responses)
        
        # Process single question
        processed_question = self._preprocess_question(question)
        return self._generate_response(processed_question)
    
    def _generate_response(self, question: str) -> str:
        """Generate response for a single processed question"""
        # Find most relevant FAQs
        similar_faqs = self._find_most_similar(question)
        
        if not similar_faqs or similar_faqs[0][1] < 0.5:
            self.unanswered_questions.append(question)
            logging.warning(f"No relevant answer found for: {question}")
            return ("I'm not quite sure about that. Could you rephrase your question? "
                   "Alternatively, you can visit our FAQ page at https://support.highrise.game/en/")
        
        # Construct context from similar FAQs
        context = "\n\n".join([
            f"Title: {self.processed_faqs[idx]['title']}\n"
            f"Content: {self.processed_faqs[idx]['content']}\n"
            f"Source: {self.processed_faqs[idx]['url']}"
            for idx, _ in similar_faqs
        ])
        
        # Generate response using GPT
        prompt = f"""You are a friendly and helpful assistant for the Highrise game. Use the following FAQ entries to answer the user's question.
If you can't find a relevant answer in the provided FAQ entries, ask for clarification or suggest visiting the FAQ website.

Previous conversation:
{self._format_conversation_history()}

FAQ Entries:
{context}

User Question: {question}

Please provide a clear, concise, and friendly answer based on the FAQ entries above. Include the source URL if relevant.
If the question is unclear, ask for clarification. If you're not sure about something, be honest about it."""
        
        try:
            response = self.llm.invoke(prompt)
            
            # Log interaction
            self.conversation_history.append({
                "question": question,
                "answer": response.content,
                "timestamp": datetime.now().isoformat(),
                "sources": [self.processed_faqs[idx]['url'] for idx, _ in similar_faqs]
            })
            
            logging.info(f"Generated response for question: {question}")
            return response.content
            
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response. Please try asking your question again."
    
    def _is_greeting(self, text: str) -> bool:
        """Check if text is a greeting"""
        greetings = {'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'}
        return text.lower().strip().rstrip('?!.') in greetings
    
    def _is_goodbye(self, text: str) -> bool:
        """Check if text is a farewell"""
        goodbyes = {'bye', 'goodbye', 'see you', 'farewell', 'thanks', 'thank you'}
        return text.lower().strip().rstrip('?!.') in goodbyes
    
    def _format_conversation_history(self) -> str:
        """Format recent conversation history"""
        # Keep only last 3 interactions for context
        recent_history = self.conversation_history[-3:] if self.conversation_history else []
        return "\n".join([
            f"User: {interaction['question']}\nAssistant: {interaction['answer']}\n"
            for interaction in recent_history
        ])
    
    def get_unanswered_questions(self) -> List[str]:
        """Return list of questions that couldn't be answered"""
        return self.unanswered_questions
    
    async def handle_message(self, message: str, session_id: str = None) -> dict:
        """Handle incoming message and return response with metadata"""
        try:
            response = self.ask(message)
            
            # Store session data if needed
            if session_id:
                self.session_data[session_id] = {
                    'last_message': message,
                    'last_response': response,
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'message': response,
                'session_id': session_id or str(int(time.time())),
                'status': 'success'
            }
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            return {
                'message': "I'm sorry, I encountered an error processing your message.",
                'session_id': session_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def store_feedback(self, feedback_data: dict) -> bool:
        """Store user feedback"""
        try:
            # Add feedback storage logic here
            logging.info(f"Feedback received: {feedback_data}")
            return True
        except Exception as e:
            logging.error(f"Error storing feedback: {str(e)}")
            return False

def main():
    # Initialize chatbot
    chatbot = SimpleFAQChatbot('data/highrise_faq.json')
    
    print("Highrise FAQ Chatbot initialized! Type 'quit' to exit.")
    
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        try:
            answer = chatbot.ask(question)
            print(f"\nAnswer: {answer}")
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try asking your question in a different way.")

if __name__ == "__main__":
    main()