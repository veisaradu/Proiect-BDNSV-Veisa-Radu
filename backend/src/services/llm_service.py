import os
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

class LLMService:
    def __init__(self):
        self.use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        self.llm = None

        if self.use_local:
            print(" Using simple extractive summarization (Local Mode forced)")
        else:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.llm = ChatGroq(
                        temperature=0.3,
                        model_name="llama-3.1-8b-instant", 
                        api_key=api_key
                    )
                    print(" LLM initialized: Groq (Llama 3.1 8B Instant)")
                except Exception as e:
                    print(f" Failed to initialize Groq: {e}")
                    self.llm = None
            else:
                print(" No GROQ_API_KEY found, defaulting to local mode")
    
    def summarize(self, texts: List[str], max_length: int = 500) -> str:
        if not texts: return "No content."
        combined = "\n\n".join(texts[:5])
        
        if self.llm:
            try:
                prompt = PromptTemplate(
                    input_variables=["text", "max_length"],
                    template="Summarize the following text concisely in {max_length} characters or less:\n\n{text}\n\nSummary:"
                )
                chain = prompt | self.llm
                response = chain.invoke({"text": combined, "max_length": max_length})
                return response.content
            except Exception as e:
                return f"Error: {str(e)}"
        return combined[:max_length] + "..."

    def answer_question(self, query: str, context: List[str]) -> Dict:
        if not context:
            return {"answer": "No context found.", "confidence": 0.0, "sources_used": 0}
        
        combined_context = "\n\n".join(context[:3])
        
        if self.llm:
            try:
                prompt = PromptTemplate(
                    input_variables=["question", "context"],
                    template="""Answer the question based strictly on the context below. If the answer is not in the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""
                )
                
                chain = prompt | self.llm
                response = chain.invoke({"question": query, "context": combined_context})
                
                return {
                    "answer": response.content.strip(),
                    "confidence": 0.95,
                    "sources_used": len(context)
                }
            except Exception as e:
                print(f"Groq Error: {e}")
                return {"answer": f"API Error: {str(e)}", "confidence": 0.0, "sources_used": 0}
        else:
            return {
                "answer": "Local Mode: " + combined_context[:200] + "...",
                "confidence": 0.5,
                "sources_used": len(context)
            }

llm_service = None
def get_llm_service():
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service