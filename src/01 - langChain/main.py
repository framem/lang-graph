from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

# Specify the local language model
local_llm = "mistral"

# Initialize the OllamaLLM model with desired parameters
llm = OllamaLLM(model=local_llm, base_url="http://127.0.0.1:11434", format="json", temperature=0)

# Define the prompt template
template = "Question: {question}\nAnswer: Let's think step by step."
prompt = PromptTemplate.from_template(template)

# Define the chain
llm_chain = prompt | llm | StrOutputParser()

# Invoke with the correct input format
generation = llm_chain.invoke({"question": "Tell me about you"})

print(generation)