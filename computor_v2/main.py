import argparse
import logging
import sys

try:
    import readline  # noqa: F401 — enables arrow keys, history, cursor movement
except ImportError:
    pass  # Windows: readline not available

from computor_v2.computorv2 import ComputorV2

logger = logging.getLogger("computor_v2")


def parse_args() -> argparse.Namespace:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-d", "--debug", action="store_true")
    argument_parser.add_argument("-f", "--file", type=str)
    return argument_parser.parse_args()


def run_file(computor_v2: ComputorV2, path: str, debug: bool = False) -> None:
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if debug:
                print(f">> {line}")
            computor_v2.add_input(line)


def run_repl(computor_v2: ComputorV2) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    while True:
        try:
            user_input = input("> ")
        except KeyboardInterrupt:
            print("")
            continue
        except EOFError:
            print("\nBye!")
            break
        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input == "exit":
            print("\nSee you later!")
            break
        computor_v2.add_input(user_input)


def main():
    args = parse_args()
    computor_v2 = ComputorV2()
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(name)s: %(message)s",
        )
        logger.debug("Debug mode enabled. Args: %s", args)
    if args.file:
        run_file(computor_v2, args.file, debug=args.debug)
    else:
        run_repl(computor_v2)


if __name__ == "__main__":
    main()
