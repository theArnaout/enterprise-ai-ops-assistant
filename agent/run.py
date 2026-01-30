import os

from agent.agent import ask_agent
from agent.config import CONVERSATION_HISTORY_SIZE


def main():
    print("AI Ops Assistant (type 'exit' to quit)\n")
    show_sql = os.environ.get("SHOW_SQL", "").strip().lower() in ("1", "true", "yes")

    conversation_history: list[tuple[str, str]] = []

    while True:
        question = input("Ask a question: ")

        if question.lower() in ["exit", "quit"]:
            break

        try:
            result = ask_agent(
                question,
                return_sql=show_sql,
                conversation_history=conversation_history[-CONVERSATION_HISTORY_SIZE:] if conversation_history else None,
            )
            if isinstance(result, dict):
                summary = result["summary"]
                print("\nResult:")
                print(summary)
                if show_sql and "sql" in result:
                    print("\n--- SQL run (for manual verification) ---")
                    print(result["sql"])
                    print("---")
            else:
                summary = result
                print("\nResult:")
                print(result)
            print("\n")
            conversation_history.append((question, summary))
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
