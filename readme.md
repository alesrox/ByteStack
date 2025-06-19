# My own Programming Language
ByteStack: A new high-level and strongly-typed language on development.

## Compiler
### Compiler Usage
The compiler, written in Python, takes a .lx file and generates the corresponding bytecode for the virtual machine.
```bash
python compiler/main.py <file> <output filename>
```
Example
```bash
python compiler/main.py examples/example.lx output
```

### Compiler Flags
The compiler supports several flags for debugging and output customization:

* -l: Only print the output of the lexer stage.
* -p: Only print the output of the parser stage.
* -d: Export a human-readable version of the bytecode to output.txt.
* -b: Export the raw bytecode to output.txt for direct use with the virtual machine.

# Virtual Machine
### Compile the Virtual Machine
The Virtual Machine (./vml) is compiled for MacOS systems with ARM chips, but you can compile it for your operating system using the makefile:
```bash
make
```

### Run the Virtual Machine
After compiling, you can execute the virtual machine with a binary file as input:
<binary file>
```bash
./vml <binary file>
```
Example:
```bash
./vml output
```

## Next Step
- toString function
- filter and map functions
- Structs implementation
- Fixing some bugs


## Future features to add
- Import statement
- For each statement
- System control functions
- BigInt and BigFloat implementation
- Dictionaries or json-like-objects (like Python dicts).
- Multi-file scripts (like import statement from python or java, or #include from C/C++/C#)
- Trash collector for the Virtual Machine
- Anything else in order to improve the language
