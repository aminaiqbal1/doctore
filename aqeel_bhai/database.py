# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import LangChain components
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType # Import AgentType enum
from servises.llms import groq_llm 

# NEW: Import Union for type hinting
from typing import Union 

llm = groq_llm
Base = declarative_base()

# Your existing database URL and engine
Database_url="postgresql://neondb_owner:npg_MKz4crbWND8R@ep-rapid-lake-adnjymqy-pooler.c-2.us-east-1.aws.neon.tech/Amina?sslmode=require&channel_binding=require"
engine = create_engine(Database_url)
SessionLocal = sessionmaker(autoflush=True, bind=engine)

# ---- SQL AGENT SETUP ----
# 1. Create a SQLDatabase object from the engine
db_for_agent = SQLDatabase(engine=engine)

# 2. Create the SQL Agent Executor
# This agent connects the LLM to the database toolkit.
# verbose=True will print the agent's thought process (useful for debugging)
sql_agent_executor = create_sql_agent(
    llm=llm,
    db=db_for_agent,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    verbose=True # Keep verbose True for debugging agent's internal steps
)
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- NEW: Example of how to use the SQL Agent to get a numerical result ----

def get_patient_count_from_agent() -> Union[int, None]:#This part tells us what the function will give back (return) A number (integer) like 1, 2, or 3. It can return: Get the patient count from an any agent.
    """
    Uses the SQL Agent Executor to query the number of patients
    and returns the numerical count.
    """
    print("\n--- Invoking SQL Agent to count patients ---")
    question = "how many patients registered on database"

    try:
        # For newer LangChain versions, .invoke() is the preferred method.
        # It returns a dictionary, and the final answer is usually in the 'output' key.
        response = sql_agent_executor.invoke({"input": question})

        # The 'response' will be a dictionary. Extract the 'output' field.
        if isinstance(response, dict) and 'output' in response:
            try:
                # Attempt to convert the output to an integer
                patient_count = int(response['output'])
                print(f"\nSUCCESS: Found {patient_count} patients.")
                return patient_count
            except ValueError:
                print(f"\nWARNING: Agent returned non-numeric output: {response['output']}")
                return None
        else:
            print(f"\nERROR: Agent did not return expected dictionary format or 'output' key: {response}")
            return None

    except Exception as e:
        print(f"\nAn error occurred while running the SQL Agent: {e}")
        # Depending on the error, you might want to log it or handle it differently
        return None

