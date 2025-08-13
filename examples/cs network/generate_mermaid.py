from chat import create_workflow

app = create_workflow()

mermaid_code = app.get_graph().draw_mermaid()
with open("workflow_graph.mmd", "w") as f:
    f.write(mermaid_code)
