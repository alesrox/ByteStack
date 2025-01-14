import sys
import struct
import tools
from utils import opcodes
from lexer import lexer
from parser import Parser
from bytecode_gen import ByteCodeCompiler

if __name__ == "__main__":
    sys.tracebacklimit = 0
    if len(sys.argv) < 2: raise Exception("File to compile is needed")

    file = open(sys.argv[1])
    only_lexer = '-l' in sys.argv
    only_parser = '-p' in sys.argv
    bytecode_doc = '-d' in sys.argv
    bytecode_doc_bin = '-b' in sys.argv

    if len(sys.argv) > 2 and len(sys.argv[-1]) > 2:
        output_file_name = sys.argv[-1]
    else:
        output_file_name = 'output.o'

    data = file.read()
    lexer.input(data)
    if only_lexer:
        tools.pretty_print(list(lexer))
        exit()

    parser = Parser(lexer)
    ast = parser.get_program()
    if only_parser:
        tools.pretty_print(ast.to_dict())
        exit()
    
    compiler = ByteCodeCompiler()
    compiler.generate_bytecode(ast)

    if bytecode_doc or bytecode_doc_bin:
        with open("output.txt", "w") as file:
            for element in compiler.get_bytecode():
                instr = element[0]
                arg = element[1]
                instr = tools.get_key(opcodes, instr) if bytecode_doc else str(instr)
                file.write(instr)
                file.write(f" {arg}\n")
        exit()

    with open(output_file_name, "wb") as file:
        for opcode, arg in compiler.get_bytecode():
            file.write(opcode.to_bytes(1, byteorder='big'))

            if isinstance(arg, int):
                file.write(struct.pack("i", arg))
            elif isinstance(arg, float):
                file.write(struct.pack("f", arg))
