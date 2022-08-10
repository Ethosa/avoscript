<div align="center">

# AVOScript
### little language just for fun

</div>

## Getting Started
#### Install
```bash
git clone https://github.com/ethosa/avoscipt
cd avoscript
```
#### Launch
```bash
python avoscript.py -h
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
