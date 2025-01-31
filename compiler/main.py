import sys
import struct
import utils.tools as tools
from utils.utils import opcodes
from lexer import lexer
from parser import Parser
from bytecode_gen import ByteCodeCompiler
from utils.error import CompilationException

class Compiler:
    def __init__(self, filename, output_file="output.o"):
        self.filename = filename
        self.output_file = output_file

        self.lexer = lexer
        self.ast = None
        self.bytecode = None
    
    def generate_lexer(self):
        try:
            with open(self.filename, "r") as file:
                self.lexer.input(file.read())
        except FileNotFoundError:
            raise CompilationException(f"No such file or directory: {self.filename}")

    def generate_ast(self):
        parser = Parser(self.lexer)
        self.ast = parser.get_program()
    
    def generate_bytecode(self):
        bytecode_generator = ByteCodeCompiler()
        bytecode_generator.generate_bytecode(self.ast)
        self.bytecode = bytecode_generator.get_bytecode()

    def export_bytecode_doc(self, use_keywords: bool):
        extension = self.output_file[::-1][:4][::-1]
        if extension != '.txt': self.output_file = "output.txt"

        with open(self.output_file, "w") as file:
            for element in self.bytecode:
                instr = element[0]
                arg = element[1]
                instr = tools.get_key(opcodes, instr) if use_keywords else str(instr)
                file.write(instr)
                file.write(f" {arg}\n")

    def export_binary(self):
        with open(self.output_file, "wb") as file:
            for opcode, arg in self.bytecode:
                file.write(opcode.to_bytes(1, byteorder='big'))

                if isinstance(arg, int):
                    file.write(struct.pack("i", arg))
                elif isinstance(arg, float):
                    file.write(struct.pack("f", arg))

def exit_with_output(argument):
    tools.pretty_print(argument)
    sys.exit()

def parse_arguments():
    if len(sys.argv) < 2:
        raise Exception("File to compile is needed")

    options = {
        "only_lexer": "-l" in sys.argv,
        "only_parser": "-p" in sys.argv,
        "bytecode_doc": "-d" in sys.argv,
        "bytecode_doc_bin": "-b" in sys.argv
    }

    output_file = sys.argv[-1] if len(sys.argv) > 2 and len(sys.argv[-1]) > 2 else "output.o"
    return sys.argv[1], output_file, options

if __name__ == "__main__":
    filename, output_file, options = parse_arguments()
    
    compiler = Compiler(filename, output_file)

    compiler.generate_lexer()
    if options["only_lexer"]: 
        exit_with_output(list(compiler.lexer))

    compiler.generate_ast()
    if options["only_parser"]: 
        exit_with_output(compiler.ast.to_dict())

    compiler.generate_bytecode()

    if options["bytecode_doc"] or options["bytecode_doc_bin"]: 
        compiler.export_bytecode_doc(options["bytecode_doc"])
    else:
        compiler.export_binary()