# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from sys import exit

from src import lex, imp_parser, Signal, ENV, ENV_CONSTS, STATEMENT_LIST_LEVEL, version

from colorama import Back, Fore, Style, init

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

args = parser.parse_args()
print(args)


if args.version:
    print(f"{Fore.RED}AVOScript{Style.RESET_ALL} {Fore.CYAN}{version}{Style.RESET_ALL}")
elif args.interactive:
    Signal.NO_CREATE_LEVEL = True
    ENV.append({})
    ENV_CONSTS.append({})
    STATEMENT_LIST_LEVEL += 1
    print(
        f"Welcome to {Fore.RED}AVOScript{Fore.RESET} "
        f"{Fore.CYAN}{version}{Fore.RESET} interactive mode."
    )
    print(f"{Fore.GREEN}>>>{Fore.RESET} ", end="")
    source = input()
    while source != 'exit':
        lexed = lex(source)
        parsed = imp_parser(lexed)
        parsed.value.eval()
        print(f"{Fore.GREEN}>>>{Fore.RESET} ", end="")
        source = input()
    exit(0)
elif args.script:
    imp_parser(lex(args.script)).value.eval()
elif args.file:
    source: str
    with open(args.file, 'r', encoding='utf-8') as f:
        source = f.read()
    imp_parser(lex(source)).value.eval()
