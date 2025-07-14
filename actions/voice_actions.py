import requests
import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

logger = logging.getLogger(__name__)

class ActionProcessVoiceInput(Action):
    """Action to process voice input and integrate with RAG system"""
    
    def name(self) -> Text:
        return "action_process_voice_input"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Get transcribed text from slot
            transcribed_text = tracker.get_slot("transcribed_text")
            
            if not transcribed_text:
                dispatcher.utter_message(text="Sorry, I couldn't process your voice input. Please try again.")
                return []
            
            logger.info(f"Processing voice input: {transcribed_text}")
            
            # Process the transcribed text through RAG system
            from .rag_components.rag_response import RAGResponseGenerator
            
            try:
                rag_generator = RAGResponseGenerator()
                response = rag_generator.generate_response(
                    query=transcribed_text,
                    intent="voice_query"  # Default intent for voice queries
                )
                
                # Send response back to user
                dispatcher.utter_message(text=response)
                
                # Store successful processing
                return [
                    SlotSet("last_voice_query", transcribed_text),
                    SlotSet("last_response", response)
                ]
                
            except Exception as e:
                logger.error(f"RAG processing failed: {e}")
                dispatcher.utter_message(
                    text="I understood your question but couldn't find relevant information. Could you please rephrase?"
                )
                return [SlotSet("transcribed_text", None)]
                
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            dispatcher.utter_message(
                text="Sorry, there was an issue processing your voice input. Please try again."
            )
            return []

class ActionClearVoiceSlots(Action):
    """Action to clear voice-related slots"""
    
    def name(self) -> Text:
        return "action_clear_voice_slots"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [
            SlotSet("transcribed_text", None),
            SlotSet("last_voice_query", None),
            SlotSet("voice_recording_active", False)
        ]
