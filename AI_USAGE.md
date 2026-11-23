# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot):

## Conversation links

- Link 1: https://chatgpt.com/share/6b04c434-078c-83eb-b33a-a0dc88ca2d06

## What I used them for

- e.g. explaining argparse, debugging the date validation, generating test data
- Reviewing and verifying flight_parser.py (CLI argument parsing with argparse, exit code handling without calling sys.exit(), and logging.FileHandler cleanup with try/finally).

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
|  |  |  |
| flight_parser.py | _build_parser, main (argument parsing and logging cleanup) | Reviewed and explained |

## Key prompts

1.Pasted flight_parser.py and asked to verify the implementation against the CLI argument rules (`-i`, `-d`, `-j`, `-a`, `-o`, `-q`, `-r`), exit codes, and`logging handler cleanup.
2.

## What I changed or verified myself
I reviewed ChatGPT's feedback on argparse exit handling and logging handler cleanup, verified that main() returns exit codes `0`, `1`, and `2` cleanly without leaving handlers open, and ran the public test suite (tests/run_public_tests.py) to confirm all tests pass.

