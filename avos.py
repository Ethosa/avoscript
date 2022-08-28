# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from json import loads
from os import path
from shutil import rmtree
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
parser.add_argument(
    "-nf", "--no-fetch",
    dest="no_fetch",
    help="no fetches package data",
    action="store_true"
)
parser.add_argument(
    "upd",
    nargs="?",
    help="update packages data"
)
parser.set_defaults(
    script="",
    file="",
    add=None,
    upd=None
)


def git_clone(
        url: str,
        directory: str,
        target_dir: Optional[str] = None
):
    """Clones repo

    :param url: repo url
    :param directory: current working directory
    :param target_dir: dir to clone
    """
    if target_dir is not None:
        subprocess.run(
            f'git clone --depth 1 --no-checkout --no-tags -q {url} {target_dir}',
            shell=True, cwd=directory, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(
            f'git clone --depth 1 --no-checkout --no-tags -q {url}',
            shell=True, cwd=directory, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def git_show(
        file: str,
        outfile: str,
        directory: str,
        target_dir: Optional[str] = None
):
    """Shows file

    :param file: path to file in repo
    :param outfile: path to out file
    :param directory: working directory
    :param target_dir: repo folder if you need
    """
    if target_dir is not None:
        subprocess.run(
            f"cd {target_dir} && git show HEAD:{file} > {outfile}",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            shell=True, cwd=directory
        )
    else:
        subprocess.run(
            f"git show HEAD:{file} > {outfile}",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            shell=True, cwd=directory
        )


def fetch_pkgs(no_fetch: bool) -> dict:
    if not no_fetch:
        print(f"{Fore.LIGHTMAGENTA_EX}Fetch packages ...{Fore.RESET}")
        if not path.exists(path.join(AVOSCRIPT, 'avoscript')):
            print(f"{Fore.LIGHTMAGENTA_EX}Cloning repo ...{Fore.RESET}")
            git_clone('https://github.com/ethosa/avoscript.git', AVOSCRIPT)
            git_show('pkgs.json', '../pkgs.json', AVOSCRIPT, './avoscript')
        else:
            subprocess.run(
                'cd avoscript && git init -q && git remote add origin https://github.com/ethosa/avoscript.git && '
                'git fetch -q origin master --depth 1 --no-tags && git checkout -q origin/master -- pkgs.json && '
                'git show origin/master:pkgs.json > ../pkgs.json',
                cwd=AVOSCRIPT, shell=True
            )
        try:
            rmtree(path.join(AVOSCRIPT, 'avoscript'), True)
        except PermissionError as e:
            print(f"{Fore.LIGHTYELLOW_EX}[WARNING]:{Fore.RESET} delete error {e}")
    try:
        out = None
        with open(path.join(AVOSCRIPT, 'pkgs.json'), 'r', encoding='utf-8') as f:
            out = f.read()
        if out is not None:
            return loads(out)
        return []
    except FileNotFoundError as e:
        print(f"{Fore.LIGHTRED_EX}Need to fetch!{Fore.RESET}")
        return []


def install_package(name: str, data: List[Dict[str, str]]):
    print(f"Install {Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} package ...")
    installed = False
    _name = name.replace('-', ' ')
    for i in data:
        if 'name' in i and i['name'] == _name:
            if 'github_url' in i:
                print(f"Found {Fore.LIGHTMAGENTA_EX}Github URL{Fore.RESET}, cloning ...")
                i['name'] = i['name'].replace(' ', '_')
                git_clone(i['github_url'], PKGS, i['name'])
                git_show('init.avo', 'init.avo', PKGS, i['name'])
                git_show('readme.md', 'readme.md', PKGS, i['name'])
                installed = True
                print(
                    f"{Fore.LIGHTGREEN_EX}Successfully installed{Fore.RESET} "
                    f"{Fore.LIGHTCYAN_EX}{name}{Fore.RESET} "
                    f"{Fore.LIGHTGREEN_EX}package{Fore.RESET} "
                )
                break
            else:
                print(
                    f"{Fore.LIGHTYELLOW_EX}[WARNING]:{Fore.RESET} package "
                    f"{Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} hasn't github_url"
                )
    if not installed:
        print(
            f"{Fore.LIGHTRED_EX}[ERROR]:{Fore.RESET} package "
            f"{Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} is not exists"
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
    elif args.upd:
        fetch_pkgs(True)
    elif args.add:
        data = fetch_pkgs(args.no_fetch)
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
