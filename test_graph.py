import asyncio
from server.graph.builder import graph

async def main():
    print("🚀 Starting the ResearchPilot Graph...")
    
    # 1. Define the initial state payload
    initial_state = {
        "query": "What are the biggest web development trends in 2025?",
        "session_id": "test-session-123",
        "search_depth": "basic",
        "retry_count": 0,
        "findings": []
    }
    
    # 2. Stream the graph execution
    # astream() yields updates every time a node finishes its work
    async for output in graph.astream(initial_state, stream_mode="updates"):
        for node_name, node_state in output.items():
            print(f"\n--- 🟢 Finished Node: {node_name.upper()} ---")
            
            # Print a quick summary of what the node added to the state
            if node_name == "planner":
                print(f"Generated {len(node_state.get('sub_questions', []))} sub-questions.")
            elif node_name == "researcher":
                print(f"A researcher finished gathering data.")
            elif node_name == "critic":
                print(f"Critique scores: {node_state.get('critique', {})}")
            elif node_name == "synthesizer":
                print("Drafted the final markdown report.")
            elif node_name == "grader":
                print(f"Final Confidence Score: {node_state.get('confidence_score')}")

    print("\n✅ Research Complete!")
    
    # Let's grab the final state to see the report
    final_state = await graph.ainvoke(initial_state)
    print("\n" + "="*50)
    print("FINAL REPORT:")
    print("="*50)
    print(final_state.get("final_report", ""))

if __name__ == "__main__":
    asyncio.run(main())
