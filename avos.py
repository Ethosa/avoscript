# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from json import loads
from os import path, remove
from sys import exit
import subprocess
from typing import Dict, List, Optional

try:
    from avoscript.lexer import Lexer
    from avoscript.lexer.default import ENV, ENV_CONSTS, LevelIndex
    from avoscript import version, AVOSCRIPT, PKGS
    from avoscript.parser import imp_parser
    from avoscript.lexer.types import Signal
except ImportError:
    from src.avoscript.lexer import Lexer
    from src.avoscript.lexer.default import ENV, ENV_CONSTS, LevelIndex
    from src.avoscript import version, AVOSCRIPT, PKGS
    from src.avoscript.parser import imp_parser
    from src.avoscript.lexer.types import Signal

from colorama import Fore, init

init(autoreset=True)
parser = ArgumentParser(
    "avoscript",
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
parser.add_argument(
    "add",
    nargs='*',
    help="install package"
)
parser.set_defaults(
    script="",
    file="",
    add=None
)


def git_clone(
        url: str,
        directory: str,
        target_dir: Optional[str] = None
):
    if target_dir is not None:
        subprocess.run(
            f'git clone --depth 1 --no-checkout --no-tags -q {url} {target_dir}',
            shell=True,
            cwd=directory
        )
    else:
        subprocess.run(
            f'git clone --depth 1 --no-checkout --no-tags -q {url}',
            shell=True,
            cwd=directory
        )


def fetch_pkgs() -> dict:
    print(f"Fetch packages data ...")
    git_clone('https://github.com/ethosa/avoscript.git', AVOSCRIPT)
    subprocess.run(
        'cd ./avoscript && git show HEAD:pkgs.json > ../pkgs.json',
        shell=True,
        cwd=AVOSCRIPT
    )
    try:
        remove(path.join(AVOSCRIPT, 'avoscript'))
    except PermissionError as e:
        print(f"{Fore.LIGHTYELLOW_EX}[WARNING]:{Fore.RESET} delete error {e}")
    with open(path.join(AVOSCRIPT, 'pkgs.json'), 'r', encoding='utf-8') as f:
        return loads(f.read())


def install_package(name: str, data: List[Dict[str, str]]):
    print(f"install {Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} package ...")
    installed = False
    for i in data:
        if 'name' in i and i['name'] == name:
            if 'github_url' in i:
                i['name'] = i['name'].replace(' ', '_')
                git_clone(i['github_url'], PKGS, i['name'])
                subprocess.run(
                    f'cd {i["name"]} && git show HEAD:init.avo > init.avo',
                    shell=True,
                    cwd=PKGS
                )
                installed = True
                break
            else:
                print(
                    f"{Fore.LIGHTYELLOW_EX}[WARNING]:{Fore.RESET} package {Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} "
                    "hasn't github_url"
                )
    if not installed:
        print(
            f"{Fore.LIGHTRED_EX}[ERROR]:{Fore.RESET} package {Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} is not exists"
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
    elif args.add:
        data = fetch_pkgs()
        for i in args.add[1:]:
            install_package(i, data)
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
