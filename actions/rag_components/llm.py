from langchain_google_genai import ChatGoogleGenerativeAI

class LLM:

    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Initializing Google Generative AI LLM...")
            try:
                cls._instance = ChatGoogleGenerativeAI(
                    model_name="gemini-1.5-flash",
                    temperature=0.1,
                    max_output_tokens=1024,
                )
                print("Google Generative AI LLM initialized successfully.")
            except Exception as e:
                print(f"Error initializing Google Generative AI LLM: {e}")
                raise
        return cls._instance
        