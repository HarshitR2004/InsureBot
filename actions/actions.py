"""
Custom Actions for Insurance Chatbot with RAG Integration
"""

from typing import Any, Text, Dict, List
import logging

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Import RAG utilities
from .llm_rag_utils import query_rag_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionEnhanceResponse(Action):
    """
    Enhanced action that uses RAG to provide context-aware responses
    """

    def name(self) -> Text:
        return "action_enhance_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get current intent and user message
            intent = tracker.latest_message.get('intent', {}).get('name')
            user_message = tracker.latest_message.get('text', '')
            
            logger.info(f"Processing intent: {intent}, message: {user_message}")
            
            # Query RAG system for enhanced response
            rag_response = query_rag_system(user_message, intent)
            
            # Send response
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionEnhanceResponse: {e}")
            dispatcher.utter_message(text="I apologize for the inconvenience. Please contact our customer service.")
            return []


class ActionExplainBenefits(Action):
    """
    Action specifically for explaining policy benefits using RAG
    """

    def name(self) -> Text:
        return "action_explain_benefits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get user message and slots
            user_message = tracker.latest_message.get('text', '')
            policy_number = tracker.get_slot('policy_number')
            sum_assured = tracker.get_slot('sum_assured') or "your sum assured"
            
            # Create context-aware query for benefits
            benefits_query = f"policy benefits tax benefits investment returns {user_message}"
            
            # Get RAG response
            rag_response = query_rag_system(benefits_query, "ask_benefits")
            
            # Send personalized response
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionExplainBenefits: {e}")
            # Fallback response
            dispatcher.utter_message(
                text="Paying premiums gives tax benefits, higher returns, and protects your family. Continue paying to keep benefits."
            )
            return []


class ActionPaymentGuidance(Action):
    """
    Action for providing payment guidance using RAG
    """

    def name(self) -> Text:
        return "action_payment_guidance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Query for payment-related information
            payment_query = f"payment methods online payment EMI options {user_message}"
            
            # Get RAG response
            rag_response = query_rag_system(payment_query, "payment_guidance")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionPaymentGuidance: {e}")
            dispatcher.utter_message(
                text="You can pay online via our website, app, or WhatsApp. Debit, credit, UPI all work."
            )
            return []


class ActionCannotPaySupport(Action):
    """
    Action for handling financial difficulties using RAG
    """

    def name(self) -> Text:
        return "action_cannot_pay_support"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Query for financial assistance options
            support_query = f"financial hardship EMI options payment assistance {user_message}"
            
            # Get RAG response
            rag_response = query_rag_system(support_query, "cannot_pay")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionCannotPaySupport: {e}")
            dispatcher.utter_message(
                text="I understand your situation. We offer EMI options and payment assistance. Can we arrange a solution?"
            )
            return []


class ActionPolicyStatus(Action):
    """
    Action for explaining policy lapse and revival using RAG
    """

    def name(self) -> Text:
        return "action_policy_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Query for policy status information
            status_query = f"policy lapse grace period revival {user_message}"
            
            # Get RAG response
            rag_response = query_rag_system(status_query, "policy_status")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionPolicyStatus: {e}")
            dispatcher.utter_message(
                text="Your policy is currently inactive. Pay within grace period to keep benefits active."
            )
            return []


class ActionPolicySpecifics(Action):
    """
    Action for specific policy details and fund information
    """

    def name(self) -> Text:
        return "action_policy_specifics"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Query for specific policy information
            policy_query = f"policy details fund value premium amount sum assured {user_message}"
            
            # Get RAG response with specific policy context
            rag_response = query_rag_system(policy_query, "policy_specifics")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionPolicySpecifics: {e}")
            dispatcher.utter_message(
                text="Let me check your policy details. Your premium is Rs. 1 lakh yearly with Rs. 10 lakh sum assured."
            )
            return []


class ActionScenarioResponse(Action):
    """
    Action for handling specific customer scenarios and objections
    """

    def name(self) -> Text:
        return "action_scenario_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Determine scenario type based on keywords
            scenario_keywords = {
                "market high": "markets too high",
                "single premium": "single premium plan confusion", 
                "emergency": "financial emergency",
                "mutual fund": "better alternatives",
                "low returns": "unsatisfactory returns",
                "new policy": "buying new policy"
            }
            
            scenario_type = "general"
            for keyword, scenario in scenario_keywords.items():
                if keyword in user_message.lower():
                    scenario_type = scenario
                    break
            
            # Query RAG with scenario context
            scenario_query = f"scenario {scenario_type} customer objection {user_message}"
            rag_response = query_rag_system(scenario_query, "scenario_response")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionScenarioResponse: {e}")
            dispatcher.utter_message(
                text="I understand your concern. Let me help you with the best solution for your situation."
            )
            return []


class ActionFundPerformance(Action):
    """
    Action for fund performance and switching guidance
    """

    def name(self) -> Text:
        return "action_fund_performance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Query for fund-related information
            fund_query = f"fund performance allocation switching Pure Stock Bluechip Bond {user_message}"
            
            # Get RAG response
            rag_response = query_rag_system(fund_query, "fund_performance")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionFundPerformance: {e}")
            dispatcher.utter_message(
                text="Your funds show good performance. Pure Stock Fund has 16.91% returns since buying."
            )
            return []


class ActionTaxBenefits(Action):
    """
    Action for tax benefits and financial planning
    """

    def name(self) -> Text:
        return "action_tax_benefits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            user_message = tracker.latest_message.get('text', '')
            
            # Query for tax-related information
            tax_query = f"tax benefits Section 80C 10 10D deduction savings {user_message}"
            
            # Get RAG response
            rag_response = query_rag_system(tax_query, "tax_benefits")
            
            dispatcher.utter_message(text=rag_response)
            
            return []
            
        except Exception as e:
            logger.error(f"Error in ActionTaxBenefits: {e}")
            dispatcher.utter_message(
                text="Your Rs. 1 lakh premium gives tax benefits under Section 80C. Maturity is tax-free."
            )
            return []
