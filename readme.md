<div align="center">

# AVOScript
### little language just for fun
requires python `3.10.x`!

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
python avoscript.py -h
```
flags
- `-v`/`--version` AVOScript version
  ```bash
  python avoscript.py -v
  ```
- `-i`/`--interactive` interactive mode
  ```bash
  python avoscript.py -i
  ```
- `-s`/`--script` execute script
  ```bash
  python avoscript.py -s "var a = 1; echo a;"
  ```
- `-f`/`--file` execute code from file
  ```bash
  python avoscript.py -f tests/test_code.avo
  ```

## Available Statements

- built-in types:
  - `string`
    ```
    var s = "My " + "string"
    ```
  - `integer`
    ```
    var i = 1 + 2 * 5;
    ```
  - `float`
    ```
    var f = 0.25 / 2.0;
    ```
  - `boolean`
    ```
    var b = true;
    ```
  - `array`
    ```
    var arr = [
      0,
      3.14,
      "Hello, world",
      true, [
        "array in other array"
      ]
    ]
    var second_element = arr[1]
    ```
- `if-elif-else`
  ```
  if false {
    echo 1;
  } elif 3 > 2 and 3 < 2 {
    echo 2;
  } elif 2 > 5 {
    echo 3;
  } else {
    echo 0;
  }
  ```
- `echo`
  ```
  var i = 10;
  echo 1, true, 2 > 3, i;  # separated by " "
  ```
- `while`
  ```
  var i = 0;
  while i < 10 {
    if i == 2 {
      continue;
    } elif i == 5 {
      break;
    }
    ++i;
  }
  ```
- `for`
  ```
  for var i = 0; i <= 5; ++i {
    echo "C-like syntax", i
  }
  for i in [5, "OK", 3.14159, [], false] {
    echo "Python-like syntax", i
  }
  ```
- `func`
  ```
  func factorial(num) {
    var i = 1;
    var result = 1;
    while i <= num {
      result *= i;
      ++i;
    }
    return result;
  }
  echo 5, factorial(5);
  
  func kwargs(a, b=3.14159, name="Andrew") {
    echo "arguments is", a, b, name
  }
  kwargs(0);
  kwargs(0, name="Ethosa");
  ```
- `import`
  ```
  import MODULE_NAME
  import math
  from module import MyObj, MyObj2
  
  var x = MyObj();
  x::smth();
  
  some_function_from_module();
  pow(...);  # can throw error
  # ok
  math.pow(...);
  MODULE_NAME.pow(...);
  ```
- `switch-case-else`
  ```
  var i = "hi";
  switch i {
    case 0 {  # i == 0
      echo "... ok";
    }
    case [1, 2, 1023] {  # i in [1, 2, 1023]
      echo "no no no";
    }
    case "hi" {  # i == "hi"
     echo "yes";
    }
    else {}  # otherwise (optionally)
  }
  
  # result from switch case
  var result = switch i {
    case "hi" {"hello, man";}
  }
  echo result;
  ```
- `ternary operator`
  ```
  # CONDITION ? TRUE_STMT : FALSE_STMT
  # TRUE_STMT if CONDITION else FALSE_STMT
  var i = 1 > 2 ? "what ..." : "okay";
  echo i;
  i = "okay" if 2 > 1 else "what ..."
  echo i;
  ```
- `lambda`
  ```
  var a = (a) => {
    echo a, "lambda is cool";
  }
  a(5);
  ```
- `class`
  ```
  class Animal {
    func say() {
    }
  }
  class Cat : Animal {
    func say() {
      echo "meow";
    }
  }
  class Dog : Animal {
    func say() {
      echo "woof";
    }
  }
  var a1 = Animal();
  var a2 = Cat();
  var a3 = Dog();
  a1::say();
  a2::say();
  a3::say();
  ```
