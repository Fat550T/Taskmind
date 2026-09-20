import sys
import json
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from graph.build_graph import build_graph

ticket_id = sys.argv[1] if len(sys.argv) > 1 else "SCRUM-9"
repo_path = "C:/Users/torch/taskmind-project/publisher-appTest"

config = {"configurable": {"thread_id": ticket_id}}


def handle_interrupts(graph, result, config):
    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value

        if isinstance(payload, dict) and "question" in payload:
            print(f"\n>>> SpecKit clarify — round {payload.get('round')} <<<")
            print(payload["question"])
            answer = input("\nTa réponse : ")
            result = graph.invoke(Command(resume=answer), config=config)
            continue

        if isinstance(payload, dict) and "message" in payload:
            print(f"\n>>> {payload['message']} <<<")
            for key, value in payload.items():
                if key != "message":
                    print(f"{key}: {value}")
            answer = input("\nApprouver ? (approved / changes_requested) : ").strip()
            result = graph.invoke(Command(resume=answer), config=config)
            continue

        print(f"\n>>> INTERRUPTION NON RECONNUE <<<\n{payload}\n")
        return result

    return result


with SqliteSaver.from_conn_string("taskmind_checkpoints.sqlite") as checkpointer:
    graph = build_graph(checkpointer)

    result = graph.invoke({"ticket_id": ticket_id, "repo_path": repo_path}, config=config)
    result = handle_interrupts(graph, result, config)

    if "__interrupt__" not in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))