# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from sys import exit

try:
    from avoscript import Lexer, imp_parser, Signal, ENV, ENV_CONSTS, version
except ImportError:
    from src import Lexer, imp_parser, Signal, ENV, ENV_CONSTS, version

from colorama import Fore, init

init(autoreset=True)
parser = ArgumentParser(
    "avoscript",
    usage="avocat [-h] [-v] [-i] [-s] [-f]",
    description=f"{Fore.RED}AVOScript{Fore.RESET} interpreter",
)
parser.add_argument(
    "-i", "--interactive",
    help="start interactive mode",
    action="store_true"
)
parser.add_argument(
    "-v", "--version",
    help="show avoscript version",
    action="store_true"
)
parser.add_argument(
    "-s", "--script",
    help="execute script"
)
parser.add_argument(
    "-f", "--file",
    help="execute file script"
)
parser.set_defaults(
    script="",
    file=""
)


def main():
    try:
        from avoscript import STATEMENT_LIST_LEVEL
    except ImportError:
        from src import STATEMENT_LIST_LEVEL
    args = parser.parse_args()
    Signal.NEED_FREE = False

    if args.version:
        print(f"{Fore.RED}AVOScript{Fore.RESET} {Fore.CYAN}{version}{Fore.RESET}")
    elif args.interactive:
        print(
            f"Welcome to {Fore.RED}AVOScript{Fore.RESET} "
            f"{Fore.CYAN}{version}{Fore.RESET} interactive mode."
        )
        print(f"{Fore.GREEN}>>>{Fore.RESET} ", end="")
        source = input()
        STATEMENT_LIST_LEVEL += 1
        ENV.append({})
        ENV_CONSTS.append({})
        while source != 'exit':
            imp_parser(Lexer.lex(source)).value.eval()
            print(f"{Fore.GREEN}>>>{Fore.RESET} ", end="")
            source = input()
        exit(0)
    elif args.script:
        imp_parser(Lexer.lex(args.script)).value.eval()
    elif args.file:
        imp_parser(Lexer.lex_file(args.file)).value.eval()


if __name__ == '__main__':
    main()
