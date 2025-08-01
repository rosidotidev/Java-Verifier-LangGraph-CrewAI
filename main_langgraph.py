import os
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from typing import TypedDict, Annotated  # Import TypedDict and Annotated
from langgraph.types import Command
from langchain_openai import OpenAI
from IPython.display import Image, display
# Ensure your OpenAI API Key is set in environment variable OPENAI_API_KEY
load_dotenv()
# Define your state schema
class CodeState(TypedDict):
    code: str
    is_correct: bool
class JavaVerifierGraph(StateGraph):
    def __init__(self):
        # Initialize LangChain OpenAI wrapper (reads OPENAI_API_KEY from env)
        self.llm = OpenAI(model="gpt-4o-mini", temperature=0)
        workflow = StateGraph(CodeState)
        workflow.add_node("start_analysis_node", self.start_analysis_node)
        workflow.add_node("optimize_code_node", self.optimize_code_node)
        workflow.add_node("correct_code_node", self.correct_code_node)

        # Define entry and transitions
        workflow.set_entry_point("start_analysis_node")
        # Conditional edges from analyzer node
        workflow.add_conditional_edges("start_analysis_node",
                                       self.conditional_next_node,
                                       {"optimize_code_node": "optimize_code_node",
                                        "correct_code_node": "correct_code_node"})
        # Cycle back from corrector to analyzer
        workflow.add_edge("correct_code_node", "start_analysis_node")
        self.graph = workflow.compile()



    def llm_check_code_syntax(self,code: str) -> bool:
        prompt = (
            "Check if the following Java code is syntactically correct. "
            "Reply ONLY with 'correct' or 'incorrect'.\n\n"
            f"Java code:\n{code}\n\nAnswer:"
        )
        result = self.llm(prompt)
        return result.strip().lower() == "correct"

    def llm_correct_code(self,code: str) -> str:
        prompt = (
            "Correct the following Java code to be syntactically valid. "
            "Provide only the corrected code without explanations.\n\n"
            f"Java code:\n{code}\n\nCorrected Java code:"
        )
        return self.llm(prompt).strip()

    def llm_optimize_code(self,code: str) -> str:
        prompt = (
            "Optimize the following syntactically correct Java code "
            "for readability and performance. Return only Java code with no explanation and no markdown.\n\n"
            f"Java code:\n{code}\n\nOptimized Java code:"
        )
        return self.llm(prompt).strip()

    # The analyzer node sets 'is_correct' in state to guide conditional branching,
    # no explicit goto inside the node function.
    def start_analysis_node(self,state:CodeState):
        code = state["code"]
        print("Analyzer: Checking syntax via LLM...")
        is_correct = self.llm_check_code_syntax(code)
        print(f"Analyzer: Code is {'correct' if is_correct else 'incorrect'}")
        return Command(update={"is_correct": is_correct})

    # Optimizer node - performs optimization and ends the workflow.
    def optimize_code_node(self,state:CodeState):
        code = state["code"]
        print("Optimizer: Optimizing code via LLM...")
        optimized_code = self.llm_optimize_code(code)
        print("Optimizer: Optimization complete. Ending workflow.")
        return Command(update={"code": optimized_code}, goto=END)

    # Corrector node - fixes syntax errors; no goto, flow cycles via explicit edge.
    def correct_code_node(self,state:CodeState):
        code = state["code"]
        print("Corrector: Correcting code via LLM...")
        corrected_code = self.llm_correct_code(code)
        print("Corrector: Correction complete. Returning to analyzer.")
        return Command(update={"code": corrected_code})

    # Branching function to decide next node after analyzer based on 'is_correct'.
    def conditional_next_node(self,state:CodeState):
        return "optimize_code_node" if state.get("is_correct") else "correct_code_node"

    def run_workflow(self,code):
        initial_state = {
            "code": code,
            "is_correct": True  # 'analyzer' will set this value at the beginning
        }

        print("Starting the execution of the workflow with invoke()...\n")

        # Run the workflow and get the final state
        final_state = self.graph.invoke(initial_state)

        print("\nWorkflow completed!")
        print("-" * 50)
        print("Final Java code (corrected and optimized):\n")
        print(final_state["code"])
        print("-" * 50)
        print(f"Final 'is_correct' state: {final_state['is_correct']}")

    def get_graph(self):
        return self.graph.get_graph()


def run_code_validation_flow():

    initial_code = """
    public class Test {
        public static void main(String[] args) {
            System.out.println("Hello World!")
        }
    }
    """

    initial_state = {
        "code": initial_code,
        "is_correct": True  # 'analyzer' will set this value at the beginning
    }

    print("Starting the execution of the workflow with invoke()...\n")

    graph=JavaVerifierGraph()
    final_state = graph.run_workflow(initial_state)


    return graph

if __name__ == "__main__":
    graph=run_code_validation_flow()
    # This command generates the PNG data as bytes, which works outside of Jupyter
    mermaid_png_bytes = graph.get_graph().draw_mermaid_png()

    # Specify the filename for the output image
    output_filename = "langgraph_workflow.png"

    try:
        # Open the file in binary write mode ('wb')
        with open(output_filename, "wb") as f:
            # Write the image bytes to the file
            f.write(mermaid_png_bytes)
        print(f"Diagram sevaed on {output_filename}")
    except Exception as e:
        print(f"Error during diagram generation: {e}")

