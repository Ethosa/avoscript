# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from sys import exit

from src import lex, imp_parser, Signal, ENV, ENV_CONSTS, STATEMENT_LIST_LEVEL, version

from colorama import Back, Fore, Style, init

init(autoreset=True)
parser = ArgumentParser(
    "avoscript",
    description="AVOScript interpreter"
)
parser.add_argument(
    "-i", "--interactive",
    help="start interactive mode",
    action="store_true"
)

parser.add_argument(
    "-s", "--script",
    help="eval script"
)

args = parser.parse_args()


if args.interactive:
    Signal.NO_CREATE_LEVEL = True
    ENV.append({})
    ENV_CONSTS.append({})
    STATEMENT_LIST_LEVEL += 1
    print(
        f"Welcome to {Fore.RED}AVOScript{Style.RESET_ALL} "
        f"{Fore.CYAN}{version}{Style.RESET_ALL} interactive mode."
    )
    source = input(Fore.GREEN + '>>> ' + Style.RESET_ALL)
    while source != 'exit':
        lexed = lex(source)
        parsed = imp_parser(lexed)
        parsed.value.eval()
        source = input(Fore.GREEN + '>>> ' + Style.RESET_ALL)
    exit(0)
elif args.script:
    imp_parser(lex(args.script)).value.eval()
