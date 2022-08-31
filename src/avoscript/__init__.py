# -*- coding: utf-8 -*-
from os import path, mkdir
from pathlib import Path

from colorama import Fore

version = 'v0.11.5'


USER = Path.home()  # user/
AVOSCRIPT = path.join(USER, '.avoscript')  # user/.avoscript/
STD = path.join(AVOSCRIPT, 'std')  # user/.avoscript/std/
PKGS = path.join(AVOSCRIPT, 'pkgs')  # user/.avoscript/pkgs/


def create_if_not_exists(folder):
    if not path.exists(folder):
        print(f"{Fore.LIGHTYELLOW_EX}[INFO]:{Fore.RESET} create {Fore.LIGHTCYAN_EX}{folder}{Fore.RESET} folder")
        mkdir(folder)


for i in [AVOSCRIPT, STD, PKGS]:
    create_if_not_exists(i)
