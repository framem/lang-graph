import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

load_dotenv()

class AirlineSupport:
    def __init__(self):
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if llm_provider == "ollama":
            self.llm = ChatOllama(
                model=os.getenv("OLLAMA_MODEL", "mistral"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.1
            )
        else:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        self.flights_data = self._load_flights()
        self.policies = self._load_policies()
        
    def _load_flights(self):
        with open('data/flights.json', 'r') as f:
            return json.load(f)
    
    def _load_policies(self):
        with open('data/policies.txt', 'r') as f:
            return f.read()
    
    def get_flight_status(self, flight_number: str) -> str:
        """Get flight status by flight number"""
        for flight in self.flights_data:
            if flight['flight_number'].upper() == flight_number.upper():
                status = f"Flight {flight['flight_number']}: {flight['status']}"
                if flight['status'] == 'Delayed':
                    status += f" - {flight.get('delay_reason', 'Unknown reason')}"
                elif flight['status'] == 'Cancelled':
                    status += f" - {flight.get('cancellation_reason', 'Unknown reason')}"
                status += f"\nRoute: {flight['origin']} to {flight['destination']}"
                status += f"\nScheduled departure: {flight['departure_time']}"
                status += f"\nGate: {flight['gate']}"
                return status
        return f"Flight {flight_number} not found"
    
    def get_policy_info(self, query: str) -> str:
        """Get airline policy information"""
        return f"Policy information:\n{self.policies}"
    
    def create_agent(self):
        tools = [
            Tool(
                name="Flight Status",
                func=self.get_flight_status,
                description="Get flight status by flight number (e.g., AA123)"
            ),
            Tool(
                name="Policy Information",
                func=self.get_policy_info,
                description="Get airline policy information for baggage, cancellation, seats"
            )
        ]
        
        agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        return agent

def main():
    support = AirlineSupport()
    agent = support.create_agent()
    
    print("🛫 Airline Customer Support Assistant")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("How can I help you today? ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = agent.run(user_input)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()