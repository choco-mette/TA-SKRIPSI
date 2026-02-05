from sqlalchemy.orm import Session
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from app.models.models import Rule, PersonalityAI

class PromptBuilder:
    def __init__(self, db: Session):
        self.db = db

    def get_system_personality(self) -> str:
        """Fetch the active personality."""
        personality = self.db.query(PersonalityAI).first()
        return personality.content if personality else "You are a helpful AI assistant."

    def get_rules(self) -> str:
        """Fetch all active rules."""
        rules = self.db.query(Rule).filter(Rule.is_active == True).all()
        if not rules:
            return ""
        
        rule_text = "\nStrictly follow these rules:\n"
        for i, rule in enumerate(rules, 1):
            rule_text += f"{i}. {rule.content}\n"
        return rule_text

    def build_rag_prompt(self, context_chunks: List[Dict[str, Any]]) -> ChatPromptTemplate:
        """
        Constructs the final prompt template including:
        1. Personality (System)
        2. Rules (System)
        3. RAG Context (System/Context)
        4. Chat History (Placeholder)
        5. User Query (Human)
        """
        # 1. Personality & Rules
        personality_text = self.get_system_personality()
        rules_text = self.get_rules()

        # 2. Format Context from RAG
        context_text = ""
        if context_chunks:
            context_text = "\nUse the following context to answer the user's question:\n"
            for chunk in context_chunks:
                context_text += f"---\n{chunk['content']}\n"
            context_text += "---\nIf the answer is not in the context, use your general knowledge but prioritize the context.\n"

        # 3. Combine System Prompt
        full_system_prompt = f"""
{personality_text}

{rules_text}

{context_text}
"""
        
        # 4. Create Template in LangChain Format
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(full_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        return prompt
