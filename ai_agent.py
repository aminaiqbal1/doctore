import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Define state for the graph
class HealthState(TypedDict):
    problem: str
    analysis: str
    recommendations: str
    exercises: str
    disclaimer: str

# Create prompt templates
analysis_prompt = ChatPromptTemplate.from_template("""
You are a helpful AI health assistant. Analyze the following health problem:

Problem: {problem}

Provide a brief analysis of the condition. Be empathetic and understanding.
Important: This is for informational purposes only and not a substitute for professional medical advice.
""")

recommendation_prompt = ChatPromptTemplate.from_template("""
Based on this health problem: {problem}

And this analysis: {analysis}

Suggest general wellness recommendations and over-the-counter remedies if appropriate.
Focus on lifestyle changes, diet, and general wellness tips.
Do NOT prescribe prescription medications.
Be specific but safe in your recommendations.
""")

exercise_prompt = ChatPromptTemplate.from_template("""
For someone with: {problem}

Suggest appropriate exercises or physical activities that might help.
Include:
1. Gentle exercises suitable for beginners
2. Breathing exercises if relevant
3. Stretching routines
4. Duration and frequency recommendations

Make sure exercises are safe and appropriate for the condition.
""")

# Define node functions
def analyze_problem(state: HealthState) -> HealthState:
    chain = analysis_prompt | llm
    response = chain.invoke({"problem": state["problem"]})
    state["analysis"] = response.content
    return state

def generate_recommendations(state: HealthState) -> HealthState:
    chain = recommendation_prompt | llm
    response = chain.invoke({
        "problem": state["problem"],
        "analysis": state["analysis"]
    })
    state["recommendations"] = response.content
    return state

def suggest_exercises(state: HealthState) -> HealthState:
    chain = exercise_prompt | llm
    response = chain.invoke({"problem": state["problem"]})
    state["exercises"] = response.content
    return state

def add_disclaimer(state: HealthState) -> HealthState:
    state["disclaimer"] = """
    ⚠️ IMPORTANT DISCLAIMER:
    This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
    """
    return state

# Build the graph
def create_health_assistant_graph():
    workflow = StateGraph(HealthState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_problem)
    workflow.add_node("recommend", generate_recommendations)
    workflow.add_node("exercises", suggest_exercises)
    workflow.add_node("disclaimer", add_disclaimer)
    
    # Add edges
    workflow.add_edge("analyze", "recommend")
    workflow.add_edge("recommend", "exercises")
    workflow.add_edge("exercises", "disclaimer")
    workflow.add_edge("disclaimer", END)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    return workflow.compile()


# Progress analysis function
def analyze_progress(progress_entries: list, current_entry: dict) -> str:
    progress_prompt = ChatPromptTemplate.from_template("""
    Analyze the patient's progress based on their entries:
    
    Previous entries: {previous_entries}
    
    Current entry:
    - Description: {description}
    - Mood rating: {mood_rating}/10
    - Symptoms improved: {symptoms_improved}
    
    Provide encouraging feedback and suggestions for continued improvement.
    Note any positive trends or areas that need attention.
    """)
    
    chain = progress_prompt | llm
    response = chain.invoke({
        "previous_entries": str(progress_entries),
        "description": current_entry["description"],
        "mood_rating": current_entry["mood_rating"],
        "symptoms_improved": current_entry["symptoms_improved"]
    })
    
    return response.content

# Initialize the graph
health_assistant = create_health_assistant_graph()