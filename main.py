import os
import json
from dotenv import load_dotenv
from langchain.agents import create_react_agent, AgentExecutor
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.tools import Tool


load_dotenv()

class AirlineSupport:
    def __init__(self):
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if llm_provider == "ollama":
            model_name = os.getenv("OLLAMA_MODEL", "mistral:latest")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            
            print(f"🔌 Connecting to Ollama at {base_url}")
            print(f"📋 Using model: {model_name}")
            
            self.llm = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.1,
                timeout=60
            )
        # else:
            # self.llm = ChatOpenAI(
            #     model="gpt-3.5-turbo",
            #     temperature=0.1,
            #     openai_api_key=os.getenv("OPENAI_API_KEY")
            # )
        self.flights_data = self._load_flights()
        self.policies = self._load_policies()
        
    def _load_flights(self):
        with open('data/flights.json', 'r') as f:
            return json.load(f)
    
    def _load_policies(self):
        with open('data/policies.txt', 'r') as f:
            return f.read()
    
    def get_flight_status(self, flight_number: str) -> str:
        flight_number = flight_number.strip().strip("'").strip('"')

        """Get flight status by flight number"""
        print(f"🔍 Searching for flight: '{flight_number}'")
        print(f"📊 Total flights in data: {len(self.flights_data)}")

        for flight in self.flights_data:
            print(f"Comparing '{flight['flight_number']}' with '{flight_number}'")
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
                name="Flight_Status",
                func=self.get_flight_status,
                description="Get flight status by flight number (e.g., AA123)"
            ),
            Tool(
                name="Policy_Information",
                func=self.get_policy_info,
                description="Get airline policy information for baggage, cancellation, seats"
            )
        ]
        
        # Create the React prompt template
        prompt = PromptTemplate.from_template("""
You are an airline customer support assistant. Help customers with flight information and policy questions.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}
""")
        
        # Create the React agent
        agent = create_react_agent(self.llm, tools, prompt)
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor

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
            print("🤖 Processing your request...")
            response = agent.invoke({"input": user_input})
            print(f"\n{response['output']}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 If using Ollama, try: 'ollama run mistral:latest' first")
            print()

if __name__ == "__main__":
    main()


# Try queries like:
# - "What's the status of flight AA123?"
# - "What's your baggage policy?"
# - "My flight AA456 is delayed, what are my options?"