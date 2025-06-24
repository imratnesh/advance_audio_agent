from typing import TypedDict
# Remove Annotated and operator, as they are no longer needed
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from loguru import logger


# --- Agent State (Corrected) ---
class AgentState(TypedDict):
    """The state of our agent."""
    text_input: str
    # The 'response' field is now a simple string.
    # LangGraph will overwrite it by default, which is the desired behavior.
    response: str


class ConversationalAgent:
    """A simple conversational agent powered by a local Ollama model."""

    def __init__(self, model_name: str = "deepseek-r1:1.5b"):
        """
        Initializes the agent with a ChatOllama model and a compiled LangGraph.

        Args:
            model_name (str): The name of the Ollama model to use.
        """
        logger.info(f"Initializing agent with model: {model_name}")
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Builds the computational graph for the agent."""
        workflow = StateGraph(AgentState)
        workflow.add_node("generate_response", self._generate_response)
        workflow.set_entry_point("generate_response")
        workflow.add_edge("generate_response", END)
        logger.info("Compiling agent graph.")
        return workflow.compile()

    def _generate_response(self, state: AgentState) -> AgentState:
        """
        Generates a response using the LLM based on the input text.

        Args:
            state (AgentState): The current state of the agent.

        Returns:
            AgentState: The updated state with the LLM's response.
        """
        text_input = state.get("text_input")
        if not text_input:
            logger.warning("No input text found in state.")
            return {"response": "I didn't receive any text to respond to."}

        logger.info(f"Generating response for input: '{text_input}'")
        try:
            message = HumanMessage(content=text_input)
            response = self.llm.invoke([message])
            logger.success("Successfully generated response from LLM.")
            return {"response": response.content}
        except Exception as e:
            logger.error(f"Error during LLM invocation: {e}")
            return {"response": "Sorry, I encountered an error while generating a response."}

    def invoke_llm(self, text_input: str) -> str:
        """
        Invokes the agent with a given text input.

        Args:
            text_input (str): The text to process.

        Returns:
            str: The agent's response.
        """
        if not text_input:
            return "Input text cannot be empty."

        initial_state = {"text_input": text_input}
        final_state = self.graph.invoke(initial_state)
        return final_state.get("response", "No response was generated.")


# This singleton instance was causing the error on import.
# With the fix above, it will now initialize correctly.
agent_instance = ConversationalAgent()