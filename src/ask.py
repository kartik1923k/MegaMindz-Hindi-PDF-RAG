"""Ask one question against the indexed Hindi PDF."""
import argparse
from rag import answer_query, format_result


def main():
    parser = argparse.ArgumentParser(description="Ask a question about the Hindi Kalam PDF.")
    parser.add_argument("question", nargs="+", help="Question in Hindi or English")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--no-llm", action="store_true", help="Skip Ollama; show retrieved passages.")
    args = parser.parse_args()
    print(format_result(answer_query(" ".join(args.question), top_k=args.top_k, use_ollama=not args.no_llm)))

if __name__ == "__main__":
    main()
