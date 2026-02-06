from sqlalchemy.orm import Session
from langchain_core.output_parsers import StrOutputParser

from app.ai.retriever import Retriever
from app.ai.memory import ChatMemory
from app.ai.prompt_builder import PromptBuilder
from app.ai.llm import LLMService
from app.utils.logger import setup_logger, setup_llm_logger

logger = setup_logger(__name__)
llm_logger = setup_llm_logger("llm_trace")

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
        logger.info(f"Retrieving context for query: {user_message[:50]}...")
        context_chunks = self.retriever.retrieve(user_message, top_k=3)
        logger.info(f"Retrieved {len(context_chunks)} context chunks.")
        
        # Detailed LLM Trace: Context
        llm_logger.info(f"--- [START TRACE] Conversation: {conversation_id} ---")
        llm_logger.info(f"USER QUERY: {user_message}")
        
        for i, chunk in enumerate(context_chunks):
            content = chunk.get("content", "")
            # App Log (Summary)
            logger.info(f"Chunk {i+1} preview: {content[:100]}...")
            # LLM Log (Full)
            llm_logger.info(f"CONTEXT CHUNK {i+1} (Doc ID: {chunk['metadata'].get('doc_id')}): \n{content}\n")

        # 2. Get Chat History
        chat_history = self.memory.get_chat_history(conversation_id, limit=6)
        llm_logger.info(f"CHAT HISTORY: \n{chat_history}")

        # 3. Build Prompt
        # Note: prompt is a ChatPromptTemplate. To see the fully formatted prompt, 
        # we would need to invoke `.format()` but doing so manually might duplicate logic.
        # We will trust the inputs logged above delineate what goes into the prompt.
        prompt = self.prompt_builder.build_rag_prompt(context_chunks)
        
        # Log System Prompt (Rules + Personality + Context)
        if hasattr(prompt, "messages") and len(prompt.messages) > 0:
            try:
                # Attempt to extract system message template
                system_template = prompt.messages[0].prompt.template
                llm_logger.info(f"SYSTEM PROMPT (Personality + Rules + Context): \n{system_template}")
            except Exception as e:
                llm_logger.warning(f"Could not log system prompt template: {e}")

        # 4. Get LLM Model
        llm = self.llm_service.get_llm_model()

        # 5. Create Chain & Invoke
        chain = prompt | llm | StrOutputParser()
        
        logger.info("Invoking LLM Chain...")
        llm_logger.info("INVOKING CHAIN...")
        
        response = chain.invoke({
            "chat_history": chat_history,
            "input": user_message
        })
        
        # Log Output
        logger.info(f"LLM Response received successfully. Length: {len(response)} chars")
        
        llm_logger.info(f"LLM RESPONSE: \n{response}")
        llm_logger.info(f"--- [END TRACE] Conversation: {conversation_id} ---\n")

        return response
