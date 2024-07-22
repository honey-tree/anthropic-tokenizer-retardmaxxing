# %%
from anthropic import AsyncAnthropic
import argparse
import asyncio
import json
from tqdm import tqdm

from typing import Tuple


async def get_tokens(client, to_tokenize: str, model=None) -> Tuple[list[str], int]:
    """
    Model defaults to haiku
    test_tokenization.py showed they're the same, unless have unicode mixed with ascii
    """
    if model is None:
        model = "claude-3-haiku-20240307"
    tokens = []
    prefill = ""
    total_tokens_usage = 0

    while prefill != to_tokenize:
        message = await client.messages.create(
            max_tokens=1,
            temperature=0,
            system=(
                    "Print out the exact text between the <print></print> tags, wrapped up in your own <print></print> tags."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"<print>{to_tokenize}</print>",
                },
                {
                    "role": "assistant",
                    "content": f"<print>{prefill}",
                }
            ],
            model=model,
        )

        total_tokens_usage += message.usage.output_tokens
        total_tokens_usage += message.usage.input_tokens

        if len(message.content) > 0 and to_tokenize.startswith(prefill + message.content[0].text):
            prefill += message.content[0].text
            tokens.append(message.content[0].text)

    return tokens, total_tokens_usage


def tokenize_text(client, to_tokenize: str, model=None) -> Tuple[list[str], int]:
    tokens, total_tokens_usage = asyncio.run(get_tokens(client, to_tokenize, model=model))
    return tokens, total_tokens_usage


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="The text to tokenize", required=False, default=None)
    parser.add_argument("--model", help="The model to be used for inference. Use a handle from Anthropic docs.", required=False, default="claude-3-haiku-20240307")
    parser.add_argument(
        "--file",
        help="A JSONL file with several texts to be tokenized",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--disable-vocab",
        help="Disable vocabulary creation",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    assert args.text or args.file, "You must provide either a text or an input file."

    KEEP_VOCAB = not args.disable_vocab

    # Initialize the Anthropic client. Will use a key exported as ANTHROPIC_API_KEY in your environment.
    client = AsyncAnthropic()

    if args.text:  # Quick execution and print on screen
        tokens, total_tokens_usage = tokenize_text(client, args.text, args.model)
        print("Tokens:", tokens)
        print("Number of text tokens:", len(tokens))
        print("Total tokens usage (as of API):", total_tokens_usage)

        with open("anthropic_vocab.jsonl", "a") as f:
            for t in tokens:
                f.write(json.dumps({"token": t}) + "\n")

        if "".join(tokens) != args.text:
            raise Exception(
                """The tokenization resulted in a different string than the original. See below:\n\n========= Original =========\n{}\n\n\n========= Tokenized =========\n{}""".format(
                    args.text, "".join(tokens)
                )
            )

    if args.file:  # Read from file and write to file
        to_tokenize = []

        # Each line is a JSON object that should be appended to to_tokenize
        with open(args.file, "r") as f:
            for line in f:
                to_tokenize.append(json.loads(line))

        for entry in tqdm(to_tokenize):
            try:
                tokens, total_tokens_usage = tokenize_text(client, entry["text"], args.model)
                entry["tokens"] = tokens
                entry["number_of_tokens"] = len(tokens)
                entry["api_total_tokens_usage"] = total_tokens_usage
                entry["tokenization_correct"] = "".join(tokens) == entry["text"]
            except Exception as e:
                print(f"Error tokenizing text: {entry['text']}")
                print(e)

        with open(args.file.replace(".jsonl", "_tokenized.jsonl"), "w") as f:
            for entry in to_tokenize:
                f.write(json.dumps(entry) + "\n")

        with open("anthropic_vocab.jsonl", "a") as f:
            for t in set([t for entry in to_tokenize for t in entry["tokens"]]):
                f.write(json.dumps({"token": t}) + "\n")
