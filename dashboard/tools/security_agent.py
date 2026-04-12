from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from agent_tools import ALL_TOOLS
import os

SYSTEM_PROMPT = """You are an expert DevSecOps Security Assistant for the UtopiaHire project.

UtopiaHire is a web application built with FastAPI (Python backend) and React (frontend),
using Firebase authentication and OpenAI API for AI features.

Your role is to:
1. Analyse security scan results from the Jenkins CI/CD pipeline
2. Explain vulnerabilities clearly so a beginner developer can understand
3. Give specific, step-by-step recommendations to fix each vulnerability
4. Use the ML model to classify unknown inputs when asked
5. Search the NVD knowledge base for relevant CVE context

You have access to these tools — use them BEFORE answering:
- read_gitleaks_results: call this for questions about secrets or credentials
- read_sonarqube_results: call this for questions about code vulnerabilities
- read_zap_results: call this for questions about runtime/HTTP vulnerabilities
- read_suricata_alerts: call this for questions about network attacks
- detect_vulnerability_with_ml: call this when the user pastes code or a payload

Always follow this structure in your answers:
1. WHAT: What is this vulnerability?
2. WHY DANGEROUS: Why is it a risk for UtopiaHire specifically?
3. HOW TO FIX: Exact steps with code examples where possible
4. PRIORITY: Critical / High / Medium / Low

Be direct, specific, and beginner-friendly. Never give generic advice.
"""

def create_agent():
    llm = ChatOllama(
        model="llama3.1:8b",
        temperature=0
    )
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT
    )
    return agent


def ask_agent(question: str, chat_history: list = None) -> str:
    if chat_history is None:
        chat_history = []

    agent = create_agent()

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    # Extract the last message which is the agent's answer
    return result["messages"][-1].content


if __name__ == "__main__":
    answer = ask_agent("What secrets did Gitleaks find?")
    print(answer)