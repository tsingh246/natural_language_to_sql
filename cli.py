"""Small CLI to run demo queries for the project showcase."""
import argparse
import logging
from dotenv import load_dotenv

from src.nl_to_sql.config import get_settings
from src.nl_to_sql.chain import build_chain


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="NL-to-SQL demo runner")
    parser.add_argument(
        "--question",
        type=str,
        default="How Many employees are there with salary greater than 10000?",
        help="Natural language question to run",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    chain = build_chain(settings)

    try:
        result = chain.invoke({"question": args.question})
        print("\n=== Result ===\n")
        if isinstance(result, dict):
            print(result.get("answer", ""))
            if result.get("query"):
                print("\n=== SQL ===\n")
                print(result["query"])
        else:
            print(result)
    except Exception as exc:
        logging.exception("Failed to run chain: %s", exc)


if __name__ == "__main__":
    main()
