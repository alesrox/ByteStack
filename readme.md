# My own Programming Language
Lexscript: A new high-level and strongly-typed language on development

## Compile the Virtual Machine
The Virtual Machine (./vml) is compiled for MacOS systems with ARM chips, but you can compile it for your operating system using this command:
```bash
gcc vm/*.c -o vml
```

## Run the Virtual Machine
After compiling, you can execute the virtual machine with a binary file as input:
<binary file> is output.bin by default
```bash
./vml <binary file>
```
Example:
```bash
./vml output.bin
```

## Compiler Usage
The compiler, written in Python, takes a .lx file and generates the corresponding bytecode for the virtual machine.
```bash
python compiler/main.py <lex file>
```
Example
```bash
python compiler/main.py test/test3.lx
```

## Compiler Flags
The compiler supports several flags for debugging and output customization:

* -l: Only print the output of the lexer stage.
* -p: Only print the output of the parser stage.
* -d: Export a human-readable version of the bytecode to output.txt.
* -b: Export the raw bytecode to output.txt for direct use with the virtual machine.

## Future features to add
- Multi-dimensional arrays (Matrices)
- Invalid Type Assignment Errors: Implementing checks in the parser to prevent the assignment of incompatible types, such as assigning a float literal to a string var.
- Castings assigments
- Multi-file scripts (like import statement from python or java)
- R/W File functions
- System control functions
- OOP (Object-oriented Programming)
- Trash collector for the Virtual Machine
- Something else in order to improve the language
