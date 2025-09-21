"""Generate a visual representation of the LangGraph workflow"""

from langgraph.graph import StateGraph
from ai_cv_agent.graph.workflow_graph import build_workflow_graph


def visualize_workflow():
    """Create and display the workflow graph"""

    # Build the graph
    graph = build_workflow_graph()

    # Compile it
    app = graph.compile()

    # Get the mermaid representation
    mermaid_code = app.get_graph().draw_mermaid()

    print("LangGraph Workflow Visualization (Mermaid format):")
    print("=" * 50)
    print(mermaid_code)
    print("=" * 50)
    print("\nYou can paste this into https://mermaid.live to visualize the graph")

    # Save to file
    with open("docs/workflow_diagram.mmd", "w") as f:
        f.write(mermaid_code)
    print("\nMermaid diagram saved to: docs/workflow_diagram.mmd")


if __name__ == "__main__":
    visualize_workflow()
