#include "../includes/errors.h"

char* error_messages[ERR_COUNT] = {
    "\033[1;35mFileNotFound:\033[0m unable to locate the specified file.",
    "\033[1;35mRecursionOverflow:\033[0m maximum recursion depth exceeded, resulting in a stack overflow.",
    "\033[1;35mMemoryViolation:\033[0m attempted access outside of allocated bounds.",
    "\033[1;35mStackUnderflow:\033[0m attempted to pop from an empty stack.",
    "\033[1;35mStackOverflow:\033[0m attempted to push beyond the stack's maximum capacity.",
    "\033[1;35mTypeMismatch:\033[0m attempted to cast between incompatible types.",
    "\033[1;35mIndexOutOfBounds:\033[0m the specified index is outside the valid range.",
    "\033[1;35mFileOpenError:\033[0m failed to open the file, please check file permissions or path validity.",
    "\033[1;35mUnsupportedSerialization:\033[0m attempted to serialize a complex data structure in an unsupported format.",
    "\033[1;35mBinaryWriteError:\033[0m attempted to write a complex data structure to a binary file, which is not permitted.",
    "\033[1;35mUnknownError:\033[0m an unexpected error occurred, please check the logs for more details."
};

void handle_error(ErrorCode code) {
    printf("\033[1;31m!\033[0m %s (Instruction: %d)\n", error_messages[code], instr_pc_log);
    exit(EXIT_FAILURE);
}