from typing import Any, Dict, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from crewai.agent import Agent
from crewai.flow.flow import Flow, listen, start, router

load_dotenv()

class CodeValidationState(BaseModel):
    code: str = ""
    syntax_status: str = ""

class JavaCodeValidationFlow(Flow[CodeValidationState]):

    analyzer_agent = Agent(
        role="Java code syntax analyzer",
        goal="Receive Java code and reply exactly with 'correct' or 'incorrect' based on syntax.",
        backstory="You are a meticulous and precise code quality tool."
    )

    corrector_agent = Agent(
        role="Java code corrector",
        goal="Receive syntactically incorrect Java code and return corrected code with valid syntax only. Return only Java code with no explanation and no markdown",
        backstory="You are an expert Java programmer who fixes code errors.",
        verbose=True
    )

    optimizer_agent = Agent(
        role="Java code optimizer",
        goal="Receive syntactically correct Java code and optimize it for readability and performance without changing logic. Return only Java compilable code with no explanation and no markdown",
        backstory="You are a senior developer specializing in code optimization."
    )

    @start("try_again")
    def start_analysis(self):
        """Starts the workflow, sends the code to the analyzer."""
        print(f"Starting code analysis...\n {self.state.code}")
        result = self.analyzer_agent.kickoff(self.state.code)
        syntax_status = result.raw
        self.state.syntax_status = syntax_status
        print(f"Analyzer result: {syntax_status}")

    @router(start_analysis)
    def conditional_next_step(self):
        """Decides whether to proceed with correction or optimization."""
        syntax_status = self.state.syntax_status
        print(f"conditional_next_step {syntax_status}")
        if syntax_status=="correct":
            return "correct"
        else:
            return "incorrect"

    @router("incorrect")
    def correct_code_step(self):
        """Performs code correction."""
        result = self.corrector_agent.kickoff(self.state.code)
        print(f"Corrector: code corrected.\n {result.raw}")
        self.state.code = result.raw
        return "try_again"

    @listen("correct")
    def optimize_code_step(self):
        """Performs code optimization."""
        result = self.optimizer_agent.kickoff(self.state.code)
        self.state.code = result.raw
        print("Optimizer: optimization finished.")
        print("\nWorkflow complete. Final optimized code:")
        print("---" * 20)
        print(self.state.code)
        print("---" * 20)

# Example usage of the workflow
def run_code_validation_flow():
    initial_java_code = """
    public class Test {
        public static void main(String[] args) {
            System.out.println("Hello, World!"
        }
    }
    """

    flow = JavaCodeValidationFlow()

    print("Starting CrewAI Java code validation flow...\n")
    # Start the workflow and get the final result
    flow.kickoff(inputs={"code": initial_java_code})
    return flow

if __name__ == "__main__":
    flow=run_code_validation_flow()
    flow.plot('my_flow_plot')
