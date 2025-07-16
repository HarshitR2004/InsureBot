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
    "change_language": ["scenario_responses"],
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
    """Main function called by Rasa actions with intent-guided retrieval using multi-tenancy"""
    try:
        # Get LLM instance
        llm, _ = LLM.get_instance()
        
        # Get intent-based document filter
        doc_filter = get_document_filter(intent)
        
        docs = []
        
        if doc_filter and "documents" in doc_filter:
            # Search multiple specific document tenants
            target_docs = doc_filter["documents"]
            for doc_name in target_docs:
                try:
                    doc_results = DatabaseManager.search_tenant(
                        tenant_name=doc_name,
                        query=question, 
                        k=2
                    )
                    docs.extend(doc_results)
                except Exception as e:
                    logger.warning(f"Failed to search tenant {doc_name}: {e}")
                    continue
            
            # Limit total results
            docs = docs[:3]
            
        elif doc_filter and len(doc_filter) == 1 and "document_name" in doc_filter:
            # Search single specific document tenant
            doc_name = doc_filter["document_name"]
            try:
                docs = DatabaseManager.search_tenant(
                    tenant_name=doc_name,
                    query=question,
                    k=3
                )
            except Exception as e:
                logger.warning(f"Failed to search tenant {doc_name}: {e}")
                docs = []
        else:
            # Fallback to search across all known tenants if no intent mapping
            # Get all known document tenants from the intent mapping
            all_tenants = set()
            for intent_docs in INTENT_DOCUMENT_MAPPING.values():
                if isinstance(intent_docs, list):
                    all_tenants.update(intent_docs)
                else:
                    all_tenants.add(intent_docs)
            
            docs = DatabaseManager.search_all_tenants(question, list(all_tenants), k=3)
        
        if not docs:
            logger.warning(f"No documents found for intent: {intent}, question: {question}")
            return "I apologize, but I couldn't find relevant information. Could you please rephrase your question?"
        
        # Log which documents were retrieved
        retrieved_docs = [doc.metadata.get('source_file', 'Unknown') for doc in docs]
        retrieved_tenants = [doc.metadata.get('tenant', 'Unknown') for doc in docs]
        logger.info(f"Intent: {intent} -> Retrieved from tenants: {retrieved_tenants}, files: {retrieved_docs}")
        
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
        return "I apologize for the technical issue. Please try rephrasing your question or contact customer service."


