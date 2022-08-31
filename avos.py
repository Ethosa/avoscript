# -*- coding: utf-8 -*-
"""
---=== AVOScript CLI ===---
Flags:
    -v/--version      show AVOScript version
    -i/--interactive  run interactive mode
    -s/--script       run script
    -f/--file         run script file
    -vb/--verbose     enable verbose stdout
Package Manager
    add               install package
        -nf/--no-fetch  no fetch packages data
    upd               update packages data
"""
from argparse import ArgumentParser
from json import loads, dumps
from os import path
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
flags = parser.add_argument_group("Flags")
flags.add_argument(
    "-i", "--interactive",
    help="start interactive mode",
    action="store_true"
)
flags.add_argument(
    "-v", "--version",
    help="show avoscript version",
    action="store_true"
)
flags.add_argument(
    "-V", "--verbose",
    help="enables verbose mode",
    action="store_true",
)
# --== With args ==-- #
flags.add_argument(
    "-s", "--script",
    dest="script",
    metavar="<src>",
    help="execute script"
)
flags.add_argument(
    "-f", "--file",
    dest="file",
    metavar="<file>",
    help="execute file script"
)
package_manager = parser.add_argument_group("Package Manager")
package_manager.add_argument(
    "-nf", "--no-fetch",
    dest="no_fetch",
    help="disable fetching package data",
    action="store_false"
)
package_manager.add_argument(
    "--upd",
    action="store_true",
    help="update packages data"
)
package_manager.add_argument(
    "--upload",
    action="store_true",
    help="upload current project"
)
package_manager.add_argument(
    "add",
    nargs='*',
    help="install package"
)
parser.set_defaults(
    script="",
    file="",
    add=None,
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
            f'git clone --depth 1 --no-tags -q {url} {target_dir}',
            shell=True, cwd=directory, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(
            f'git clone --depth 1 --no-tags -q {url}',
            shell=True, cwd=directory, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def fetch_pkgs(no_fetch: bool, out_file: str = 'pkgs.json') -> List[Dict[str, str]]:
    """Fetches packages data

    :param no_fetch: need to fetch
    :param out_file: output file
    :return: list of packages
    """
    if not no_fetch:
        print(f"{Fore.LIGHTMAGENTA_EX}Fetch packages ...{Fore.RESET}")
        if not path.exists(path.join(AVOSCRIPT, 'avoscript')):
            print(f"{Fore.LIGHTMAGENTA_EX}Cloning repo ...{Fore.RESET}")
            git_clone('https://github.com/ethosa/avoscript.git', AVOSCRIPT)
        else:
            subprocess.run(
                'cd avoscript && git init -q && git remote add origin https://github.com/ethosa/avoscript.git && '
                'git fetch -q origin master --depth 1 --no-tags && git checkout -q origin/master -- pkgs.json && '
                f'git show origin/master:pkgs.json > {out_file}',
                cwd=AVOSCRIPT, shell=True
            )
    try:
        out = None
        with open(path.join(AVOSCRIPT, 'avoscript', out_file), 'r', encoding='utf-8') as f:
            out = f.read()
        if out is not None:
            return loads(out)
        return []
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}Need to fetch!{Fore.RESET}")
        return []


def install_package(name: str, data: List[Dict[str, str]]):
    """Install package

    :param name: package name
    :param data: package data
    """
    print(f"Install {Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET} package ...")
    installed = False
    _name = name.replace('-', ' ')
    for i in data:
        if 'name' in i and i['name'] == _name:
            if 'github_url' in i:
                print(f"Found {Fore.LIGHTMAGENTA_EX}Github URL{Fore.RESET}, cloning ...")
                i['name'] = i['name'].replace(' ', '_')
                git_clone(i['github_url'], PKGS, i['name'])
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
    signal.VERBOSE = args.verbose  # -V/--verbose
    env = [{}]
    consts = [{}]
    lvl = LevelIndex()
    lvl.inc()

    # -v/--version flag
    if args.version:
        print(f"{Fore.LIGHTRED_EX}AVOScript{Fore.RESET} {Fore.LIGHTCYAN_EX}{version}{Fore.RESET}")
    # --upload flag
    elif args.upload:
        print(f"{Fore.LIGHTYELLOW_EX}Working via Github CLI (gh){Fore.RESET}")
        package_name = input(f"{Fore.LIGHTCYAN_EX}name of package: {Fore.RESET}")
        package_description = input(f"{Fore.LIGHTCYAN_EX}package description: {Fore.RESET}")
        github_url = input(f"{Fore.LIGHTCYAN_EX}project Github URL: {Fore.RESET}")
        if not package_name:
            print(f"{Fore.LIGHTRED_EX}[ERROR]:{Fore.RESET} package name is empty")
            return
        fetch_pkgs(False)
        subprocess.run(
            f'cd avoscript && git pull -q --no-tags && git checkout -b {package_name}',
            cwd=AVOSCRIPT, shell=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        data = []
        with open(path.join(AVOSCRIPT, 'avoscript', 'pkgs.json'), 'r') as f:
            data = loads(f.read())
        data.append({
            'name': package_name.replace('-', ' '),
            'description': package_description,
            'github_url': github_url
        })
        with open(path.join(AVOSCRIPT, 'avoscript', 'pkgs.json'), 'w') as f:
            f.write(dumps(data, indent=2))
        subprocess.run(
            f'cd avoscript && '
            f'git add pkgs.json && git commit -q -m "add `{package_name}` package" && '
            f'gh pr create -t "Add `{package_name}` package" -B master -b "{package_description}" -l "new package" && '
            f'git switch master && git branch -D {package_name}',
            cwd=AVOSCRIPT, shell=True
        )
        print(f"{Fore.GREEN}PR was created{Fore.RESET}")
    # --upd flag
    elif args.upd:
        fetch_pkgs(False)
    # -i/--interactive flag
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
    # -s/--script flag
    elif args.script:
        imp_parser(Lexer.lex(args.script)).value.eval(env, consts, lvl, {}, signal)
    # -f/--file flag
    elif args.file:
        imp_parser(Lexer.lex_file(args.file)).value.eval(env, consts, lvl, {}, signal)
    # add pos arg
    elif args.add:
        data = fetch_pkgs(args.no_fetch)  # -nf/--no-fetch flag
        for i in args.add[1:]:
            install_package(i, data)


if __name__ == '__main__':
    main()
