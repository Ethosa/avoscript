<div align="center">

# AVOScript

| <br/>[![carbon (12)](https://user-images.githubusercontent.com/49402667/184539431-4cfd87eb-2631-4553-ad11-598b1dacf601.svg)](https://github.com/Ethosa/avoscript/wiki/Available-Statements) | [![carbon (11)](https://user-images.githubusercontent.com/49402667/184539434-6d32c0ff-f72f-4918-a57f-a4529e8843ab.svg)](https://github.com/Ethosa/avoscript/wiki/Available-Statements) |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

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
  python avos.py -s "var a = 1; echo(a);"
  ```
- `-f`/`--file` execute code from file
  ```bash
  python avos.py -f tests/test_code.avo
  ```

<div align="center">

| [Wiki][] | [AvailableStatements][] | [Playground][] |
|----------|-------------------------|----------------|

</div>

[Wiki]:https://github.com/Ethosa/avoscript/wiki
[AvailableStatements]:https://github.com/Ethosa/avoscript/wiki/Available-Statements
[Playground]:https://ethosa.github.io/avoscript
