<div align="center">

# AVOScript
[![carbon (3)](https://user-images.githubusercontent.com/49402667/184535093-ffdaa33d-b476-4096-8bb1-d2506f4064a3.svg)](https://github.com/Ethosa/avoscript/wiki/Available-Statements)
### little language just for fun
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/avoscript?style=flat-square)](https://pypi.project/avoscript)
[![PyPI](https://img.shields.io/pypi/v/avoscript?style=flat-square)](https://pypi.org/project/avoscript)

</div>

## Getting Started
#### Install
```bash
git clone https://github.com/ethosa/avoscipt
cd avoscript
pip install requirements.txt
```
#### Launch
```bash
python avos.py -h
```
flags
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
  python avos.py -s "var a = 1; echo a;"
  ```
- `-f`/`--file` execute code from file
  ```bash
  python avos.py -f tests/test_code.avo
  ```

<div align="center">

| [Wiki][] | [AvailableStatements][] |
|----------|-------------------------|

</div>

[Wiki]:https://github.com/Ethosa/avoscript/wiki
[AvailableStatements]:https://github.com/Ethosa/avoscript/wiki/Available-Statements
