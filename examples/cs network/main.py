from langchain_core.messages import HumanMessage
from chat import create_workflow

app = create_workflow()

if __name__ == "__main__":
    input_message = {
        "messages": [HumanMessage(content="Erzähle mir was zu Produkt 3 ")]
        # "messages": [HumanMessage(content="Gibt es aktuell Systemprobleme?")]
    }
    result = app.invoke(input_message)
    for msg in result["messages"]:
        print(f"{msg.type}: {msg.content}")
