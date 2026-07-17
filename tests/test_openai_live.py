import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def safe_print(label: str, value: str) -> None:
    printable = value.encode("ascii", errors="backslashreplace").decode("ascii")
    print(f"{label}: {printable}")


def main() -> None:
    load_dotenv()

    model_name = os.getenv("OPENAI_MODEL")
    if not model_name:
        raise RuntimeError("OPENAI_MODEL is not set in your .env file.")

    client = OpenAI()

    input = "Hi! In one sentence, please tell me how a RAG agent works."

    response = client.responses.create(
        model=model_name,
        input=input,
    )

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "openai_live_response.json"
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model_name,
        "prompt": input,
        "response": response.output_text,
    }

    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    safe_print("Model", model_name)
    safe_print("Response", response.output_text)
    safe_print("Saved to", str(output_path))


if __name__ == "__main__":
    main()
