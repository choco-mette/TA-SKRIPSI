from sqlalchemy.orm import Session
from langchain_core.output_parsers import StrOutputParser

from app.ai.retriever import Retriever
from app.ai.memory import ChatMemory
from app.ai.prompt_builder import PromptBuilder
from app.ai.llm import LLMService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class RAGPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = Retriever(db)
        self.memory = ChatMemory(db)
        self.prompt_builder = PromptBuilder(db)
        self.llm_service = LLMService(db)

    def run(self, conversation_id: str, user_message: str):
        """
        Orchestrates the full RAG pipeline:
        1. Retrieve relevant context
        2. Fetch chat history
        3. Build prompt (Personality + Rules + Context + History)
        4. Invoke LLM
        """
        logger.info(f"Starting RAG Pipeline for Conversation: {conversation_id}")
        
        # 1. Retrieve Context (RAG)
        context_chunks = self.retriever.retrieve(user_message, top_k=3)

        # 2. Get Chat History
        chat_history = self.memory.get_chat_history(conversation_id, limit=6)

        # 3. Build Prompt
        prompt = self.prompt_builder.build_rag_prompt(context_chunks)

        # 4. Get LLM Model
        llm = self.llm_service.get_llm_model()

        # 5. Create Chain & Invoke
        chain = prompt | llm | StrOutputParser()
        
        logger.info("Invoking LLM Chain...")
        response = chain.invoke({
            "chat_history": chat_history,
            "input": user_message
        })
        logger.info("LLM Response received successfully.")

        return response
