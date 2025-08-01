# Java Syntax Verifier & Optimizer using CrewAI and LangGraph

This project demonstrates how to use **CrewAI** and **LangGraph** to build an autonomous workflow capable of:

- ✅ Validating the **syntax** of Java code  
- 🛠️ Automatically correcting syntax errors  
- 🚀 Optimizing code for readability and performance  

There are **two equivalent implementations** of the same logic:

- `main_langgraph.py` — implemented using **LangGraph**
- `main_crewai_flow.py` — implemented using **CrewAI**

Both provide a working, end-to-end autonomous agent pipeline.

---

## 📦 Installation

To install the project, follow these steps:

```bash
git clone https://github.com/rosidotidev/Java-Verifier-LangGraph-CrewAI.git
cd Java-Verifier-LangGraph-CrewAI
```
run the command within setup.txt

## 🔐 Requirements

- Python 3.10 or higher  
- `OPENAI_API_KEY` set on .env file 
- Internet connection  

## ▶️ Running the Workflow

Make sure you've completed the installation steps.

```bash
 pipenv run python main_crewai_flow.py
```
or
```bash
 pipenv run python main_langgraph.py
```
