import logging
from typing import List, Optional, Dict
from langchain_core.prompts import ChatPromptTemplate
from .llm import LLM
from .vector_store import DatabaseManager

logger = logging.getLogger(__name__)

# Intent to document mapping
INTENT_DOCUMENT_MAPPING = {
    "ask_benefits": ["life_insurance_benefits", "specific_policy_details"],
    "ask_policy_details": ["specific_policy_details"],
    "cannot_pay": ["policy_lapse_revival", "payment_methods"],
    "agree_to_pay": ["payment_methods"],
    "ask_fund_performance": ["specific_policy_details"],
    "ask_tax_benefits": ["life_insurance_benefits", "specific_policy_details"],
    "market_concerns": ["scenario_responses"],
    "single_premium_confusion": ["scenario_responses"],
    "emergency_needs": ["scenario_responses", "policy_lapse_revival"],
    "compare_alternatives": ["scenario_responses"],
    "unsatisfied_returns": ["scenario_responses"],
    "want_new_policy": ["scenario_responses"],
    "policy_status": ["policy_lapse_revival"],
    "payment_guidance": ["payment_methods"],
}

# Your existing template is excellent
RAG_PROMPT = """You are **Veena**, a polite and persuasive female insurance agent at **ValuEnable Life Insurance**.

Your task is to assist customers in paying their **pending insurance premiums** by strictly following the conversation flow provided in the context below.

**Context from Policy Documents:**
{context}

**Customer Question:** {question}
**Intent:** {intent}

**Instructions:**
- Use ONLY the context provided above to answer
- Keep responses under 35 words
- Always end with a relevant question
- Be helpful, polite, and professional

**Veena's Response:**"""

def get_document_filter(intent: str) -> Optional[Dict]:
    """Get document filter based on intent"""
    if not intent or intent not in INTENT_DOCUMENT_MAPPING:
        return None
    
    target_documents = INTENT_DOCUMENT_MAPPING[intent]
    
    # Create OR filter for multiple documents
    if len(target_documents) == 1:
        return {"document_name": target_documents[0]}
    else:
        # For multiple documents, we'll search each separately and combine
        return {"documents": target_documents}

def query_rag_system(question: str, intent: str = None) -> str:
    """Main function called by Rasa actions with intent-guided retrieval"""
    try:
        # Get LLM and vector store instances
        llm = LLM.get_instance()
        vector_store = DatabaseManager.get_collection()
        
        # Get intent-based document filter
        doc_filter = get_document_filter(intent)
        
        docs = []
        
        if doc_filter and "documents" in doc_filter:
            # Search multiple specific documents
            target_docs = doc_filter["documents"]
            for doc_name in target_docs:
                doc_results = vector_store.similarity_search(
                    question, 
                    k=2,  # Reduced k since we're searching multiple docs
                    filter={"document_name": doc_name}
                )
                docs.extend(doc_results)
            
            # Limit total results
            docs = docs[:3]
            
        elif doc_filter:
            # Search single specific document
            docs = vector_store.similarity_search(
                question, 
                k=3,
                filter=doc_filter
            )
        else:
            # Fallback to general search if no intent mapping
            docs = vector_store.similarity_search(question, k=3)
        
        if not docs:
            logger.warning(f"No documents found for intent: {intent}, question: {question}")
            return _fallback_response(intent)
        
        # Log which documents were retrieved
        retrieved_docs = [doc.metadata.get('source_file', 'Unknown') for doc in docs]
        logger.info(f"Intent: {intent} -> Retrieved from: {retrieved_docs}")
        
        # Combine contexts
        context_text = "\n".join([
            f"[{doc.metadata.get('source_file', 'Policy Document')}] {doc.page_content}" 
            for doc in docs
        ])
        
        # Generate response
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
        response = llm.invoke(
            prompt.format(
                context=context_text,
                question=question,
                intent=intent or "general_query"
            )
        )
        
        # Extract and limit response
        response_text = response.content if hasattr(response, 'content') else str(response)
        words = response_text.split()
        if len(words) > 35:
            response_text = ' '.join(words[:35]) + "..."
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error in query_rag_system: {e}")
        return _fallback_response(intent)

def _fallback_response(intent: str) -> str:
    """Fallback responses when RAG fails"""
    fallbacks = {
        "ask_benefits": "Your policy offers tax benefits and life cover. Shall I explain more?",
        "cannot_pay": "I understand. We have EMI options available. Can we discuss solutions?",
        "agree_to_pay": "Great! I can help with payment. Shall I send the payment link?",
        "ask_policy_details": "Let me check your policy details. What specific information do you need?",
        "ask_fund_performance": "Your funds show good performance. Would you like specific performance numbers?",
        "ask_tax_benefits": "Your premium gives tax benefits under Section 80C. Shall I explain more?",
    }
    return fallbacks.get(intent, "I'm here to help with your insurance policy. What would you like to know?")


