<div align="center">

# AVOScript

| ![CodeExample][] | ![CLIExample][] |
|:----------------:|:---------------:|
|   Code example   |   CLI Example   |

### little language just for fun
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/avoscript?style=flat-square)](https://pypi.project/avoscript)
[![PyPI](https://img.shields.io/pypi/v/avoscript?style=flat-square)](https://pypi.org/project/avoscript)

</div>

## Getting Started!
### Install
- via pip
  ```bash
  pip install avoscript --upgrade
  ```
- via git
  ```bash
  git clone https://github.com/ethosa/avoscipt
  cd avoscript
  pip install requirements.txt
  ```

### CLI
```bash
python avos.py -h
```
#### Flags
- `-v`/`--version` AVOScript version
  ```bash
  python avos.py -v
  ```
- `-i`/`--interactive` interactive mode
  ```bash
  python avos.py -i
  ```
- `-s`/`--script` execute script
  ```bash
  python avos.py -s "var a = 1; echo(a);"
  ```
- `-f`/`--file` execute code from file
  ```bash
  python avos.py -f tests/test_code.avo
  ```

#### Package Manager
- install package
  ```bash
  python avos.py add package-name
  ```
- install package without packages fetching
  ```bash
  python avos.py add package-name -nf
  python avos.py add package-name --no-fetch
  ```
- update packages data
  ```bash
  python avos.py --upd
  ```
- upload your package
  ```bash
  python avos.py --upload
  ```

<div align="center">

| [Wiki][] | [AvailableStatements][] | [Playground][] |
|----------|-------------------------|----------------|

</div>

[Wiki]:https://github.com/Ethosa/avoscript/wiki
[AvailableStatements]:https://github.com/Ethosa/avoscript/wiki/Available-Statements
[Playground]:https://ethosa.github.io/avoscript

[CodeExample]:https://user-images.githubusercontent.com/49402667/187029351-875205bf-67f7-4dac-bed7-ca2746d65ad4.png
[CLIExample]:https://user-images.githubusercontent.com/49402667/187029349-4ee9a53e-3ad6-44f4-b2c0-be1d9cc71257.png
