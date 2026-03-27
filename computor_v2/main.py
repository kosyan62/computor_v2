import argparse
from computor_v2.computorv2 import ComputorV2


def parse_args() -> argparse.Namespace:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-d", "--debug", action="store_true")
    argument_parser.add_argument("-f", "--file", type=str)
    return argument_parser.parse_args()


def main():
    args = parse_args()
    computor_v2 = ComputorV2()
    if args.debug:
        print("Debug mode is on")
        print(f"Args: {args}")
    if args.file:
        # TODO handle single file input
        print(args.file)
    else:
        while True:
            try:
                user_input = input("> ")
            except (KeyboardInterrupt, EOFError):
                print("\nBye!")
                break
            if user_input == "exit":
                print("\nSee you later!")
                break
            computor_v2.add_input(user_input)


if __name__ == "__main__":
    main()
