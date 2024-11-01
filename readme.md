# My own Programming Language

## Compile the Virtual Machine
```bash
gcc vm/*.c -o vml
```

## Run the Virtual Machine
After compiling, you can execute the virtual machine with a binary file as input:
<binary file> is output.bin by default
```bash
./vml <binary file>
```

## Compiler Usage
The compiler, written in Python, takes a .lex file and generates the corresponding bytecode for the virtual machine.
```bash
python compiler/main.py <lex file>
```

## Compiler Flags
The compiler supports several flags for debugging and output customization:

	•	-l: Only print the output of the lexer stage.
	•	-p: Only print the output of the parser stage.
	•	-d: Export a human-readable version of the bytecode to output.txt.
	•	-b: Export the raw bytecode to output.txt for direct use with the virtual machine.
