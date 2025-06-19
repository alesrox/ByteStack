#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "structs-type.h"
#define ERR_COUNT 11

Instruction instr_pc_log;

typedef enum {
    FILE_NOT_FOUND,
    MAX_RECURSION_DEPTH_EXCEEDED,
    MEMORY_ACCESS_OUT_OF_BOUNDS,
    STACK_UNDERFLOW,
    STACK_OVERFLOW,
    TYPE_CAST_ERROR,
    INDEX_OUT_OF_BOUNDS,
    FILE_PERMISSION_ERROR,
    UNSUPPORTED_COMPLEX_TYPE_WRITE,
    UNSUPPORTED_BINARY_WRITE,
    UNDEFINED_ERROR
} ErrorCode;

extern char* error_messages[ERR_COUNT];
void handle_error(ErrorCode code);