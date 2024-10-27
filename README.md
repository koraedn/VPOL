# VPOL Documentation

## Overview

**VPOL** is a scripting language interpreter written in Python, designed for ease of use and versatility. It allows users to automate tasks related to networking, terminal manipulation, and data handling through a simple, user-friendly syntax. Developed by **koraedn**, this is version 1.0 of VPOL.

### Features

- **Variable Management**: Create and manipulate variables with ease.
- **Control Flow**: Implement conditional statements (`if`, `elseif`, `else`) to control the flow of your scripts.
- **Terminal Interactions**: Print messages, clear the terminal, and set terminal titles.
- **Networking**: Ping IP addresses, check HTTP connections, and send TCP/UDP packets.
- **JSON Parsing**: Parse and pretty-print JSON data.

## Installation

To use VPOL, ensure you have Python installed on your system along with the necessary dependencies. You can install the required libraries using pip:

```bash
pip install colorama scapy requests
```

Then run the setup.py as admin to add VPOL to path (allowing you to use vpol.py ANYWHERE)
```python
python setup.py install
```

## Getting Started

1. **Script Creation**: Create a `.vpol` script using any text editor.
2. **Script Execution**: Run your script using the command line:
    ```bash
    python vpol.py <script.vpol>
    ```

## Syntax

### Variable Assignment

Variables are defined using the `@` symbol. For example:

```plaintext
@myVar = "Hello, World!"
```

You can also define a variable without an initial value:

```plaintext
@myVar = {
  # This can be filled later
}
```

### Print to Terminal

To print content to the terminal, use:

```plaintext
terminal.print("This is a message")
```

### Conditional Statements

VPOL supports `if`, `elseif`, and `else` statements for control flow:

```plaintext
if condition:
    # code block
elseif another_condition:
    # code block
else:
    # code block
```

### Function Definition and Calling

Functions are defined using the `${functionName}` syntax and can be called with `~$functionName`.

```plaintext
${myFunction
    terminal.print("Inside my function")
}

~$myFunction  # Calling the function
```

### JSON Parsing

You can parse JSON strings with the following command:

```plaintext
json.parse('{"key": "value"}')
```

### Networking Commands

- **Ping** an IP address:

    ```plaintext
    network.ping("192.168.1.1")
    ```

- **Check HTTP connection**:

    ```plaintext
    network.http_check("http://example.com")
    ```

- **Send TCP/UDP packets**:

    ```plaintext
    network.send_packet("192.168.1.1, 80, tcp, 1024")
    ```

### Terminal Input

To take user input and assign it to a variable:

```plaintext
terminal.input("Enter your name: ") @userName
```

## Code Structure

The core of VPOL consists of several classes and methods:

### `VPOLProcessor`

This is the main class responsible for interpreting and executing the VPOL scripts. Key methods include:

- **`run(code)`**: Executes the provided code line by line.
- **`processLine(line, lineNum)`**: Processes individual lines and determines their actions.
- **`evaluateIf(line, lineNum)`**: Evaluates if conditions for control flow.
- **`callFunction(line, lineNum)`**: Executes a defined function when called.

### `TerminalUtils`

A utility class to handle terminal-specific functions like setting the terminal title.

### `VPOLException`

A custom exception class used for error handling within the VPOL interpreter.

## Example Script

Here's an example of a simple VPOL script that demonstrates its capabilities:

```plaintext
# This script demonstrates basic VPOL functionality.

# Define a function
${greet}
    terminal.print("Hello, VPOL user!")
}

# Call the function
~$greet

# Variable assignment
@user = ""
terminal.input("What is your name? ") @user

# Conditional statement
if @user == "koraedn":
    terminal.print("Welcome back, koraedn!")
elseif @user != "":
    terminal.print("Hello, " + @user + "!")
else:
    terminal.print("No name provided.")

# Networking command
network.ping("8.8.8.8")
```

## Error Handling

VPOL includes built-in error handling through the `VPOLException` class, which provides meaningful error messages for common issues such as:

- Undefined variables
- Invalid syntax in statements
- Network command failures

## Conclusion

VPOL provides a powerful yet accessible way to automate tasks and interact with your environment. As you explore its capabilities, feel free to create complex scripts that can handle a variety of tasks with minimal effort. For any issues or feature requests, feel free to reach out to **koraedn**. Happy scripting!
