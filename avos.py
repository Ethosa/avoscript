# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from sys import exit

try:
    from avoscript import Lexer, imp_parser, Signal, ENV, ENV_CONSTS, LevelIndex, version
except ImportError:
    from src import Lexer, imp_parser, Signal, ENV, ENV_CONSTS, LevelIndex, version

from colorama import Fore, init

init(autoreset=True)
parser = ArgumentParser(
    "avoscript",
    usage="avocat [-h] [-v] [-i] [-s] [-f]",
    description=f"{Fore.LIGHTRED_EX}AVOScript{Fore.RESET} {Fore.LIGHTCYAN_EX}{version}{Fore.RESET} interpreter",
)
# --== Flags ==-- #
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
    "-vb", "--verbose",
    help="enables verbose mode",
    action="store_true",
)
# --== With args ==-- #
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
    args = parser.parse_args()
    signal = Signal()
    signal.NEED_FREE = False
    signal.VERBOSE = args.verbose
    env = [{}]
    consts = [{}]
    lvl = LevelIndex()
    lvl.inc()

    if args.version:
        print(f"{Fore.LIGHTRED_EX}AVOScript{Fore.RESET} {Fore.LIGHTCYAN_EX}{version}{Fore.RESET}")
    elif args.interactive:
        print(
            f"Welcome to {Fore.LIGHTRED_EX}AVOScript{Fore.RESET} "
            f"{Fore.LIGHTCYAN_EX}{version}{Fore.RESET} interactive mode."
        )
        print(
            f"Write {Fore.LIGHTRED_EX}exit{Fore.RESET} to shutdown interactive mode."
        )
        print(f"{Fore.LIGHTGREEN_EX}>>>{Fore.RESET} ", end="")
        source = input()
        while source != 'exit':
            signal.NO_CREATE_LEVEL = True
            imp_parser(Lexer.lex(source)).value.eval(env, consts, lvl, {}, signal)
            print(f"{Fore.LIGHTGREEN_EX}>>>{Fore.RESET} ", end="")
            source = input()
        print(f"Exited via {Fore.LIGHTRED_EX}exit{Fore.RESET} command")
        exit(0)
    elif args.script:
        imp_parser(Lexer.lex(args.script)).value.eval(env, consts, lvl, {}, signal)
    elif args.file:
        imp_parser(Lexer.lex_file(args.file)).value.eval(env, consts, lvl, {}, signal)


if __name__ == '__main__':
    main()
