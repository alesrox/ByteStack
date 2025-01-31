import os
import unittest
from main import Compiler

class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.test_files = [f"examples/example{i}.lx" for i in range(7)]
        self.expected_outputs = [f"compiler/expected_outputs/output{i}.txt" for i in range(7)]
        self.output_file = "compiler/expected_outputs/output-to-check.txt"

    def test_export_bytecode_doc(self):
        for test_file, expected_file in zip(self.test_files, self.expected_outputs):
            with self.subTest(test_file=test_file):
                # Ensure the test file exists
                if not os.path.exists(test_file):
                    self.fail(f"Test file {test_file} does not exist.")
                
                # Compile the file and generate the output
                compiler = Compiler(test_file, self.output_file)
                try:
                    compiler.generate_lexer()
                    compiler.generate_ast()
                    compiler.generate_bytecode()
                    compiler.export_bytecode_doc(use_keywords=True)
                except Exception as e:
                    self.fail(f"Compilation failed for {test_file}: {e}")

                # Compare the generated output with the expected output
                with open(self.output_file, "r") as output, open(expected_file, "r") as expected:
                    self.assertEqual(output.read(), expected.read(), f"Output mismatch for {test_file}")

    def tearDown(self):
        # Clean up the generated output file
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

if __name__ == "__main__":
    unittest.main()
