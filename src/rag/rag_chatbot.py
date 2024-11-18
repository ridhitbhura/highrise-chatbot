import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain_pinecone import PineconeVectorStore

class RAGChatbot:
    def __init__(self, index_name: str, namespace: str):
        # Disable LangSmith tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        os.environ["LANGCHAIN_API_KEY"] = "not-needed"
        
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.environ.get('OPENAI_API_KEY')
        )
        
        self.vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings
        )
        
        self.llm = ChatOpenAI(
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            model_name='gpt-4',
            temperature=0.1
        )
        
        # Customize the prompt
        prompt_template = """You are a helpful assistant for Highrise game. Use the following pieces of context to answer the question at the end. If you don't know the answer or can't find it in the context, just say "I don't have information about that in my knowledge base." Don't try to make up an answer.

Context: {context}

Question: {question}

Answer: """
        
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        combine_docs_chain = create_stuff_documents_chain(
            self.llm, 
            retrieval_qa_chat_prompt
        )
        
        self.chain = create_retrieval_chain(
            self.vector_store.as_retriever(search_kwargs={"k": 5}),  # Increase number of retrieved documents
            combine_docs_chain
        )
    
    def ask(self, question: str) -> str:
        """Ask a question and get response with relevant context"""
        response = self.chain.invoke({"input": question})
        return response['answer']

# Usage example:
if __name__ == "__main__":
    chatbot = RAGChatbot('highrise-faq', 'faq')
    
    # Test the chatbot
    question = "How do I verify my account on Discord?"
    answer = chatbot.ask(question)
    print(f"Q: {question}\nA: {answer}")
