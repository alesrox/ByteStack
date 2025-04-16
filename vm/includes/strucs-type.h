#pragma once
#include <stdint.h>

typedef enum {
    UNASSIGNED_TYPE,
    BOOL_TYPE,
    INT_TYPE,
    FLOAT_TYPE,
    CHAR_TYPE,
    ARRAY_TYPE,
    OBJ_TYPE
} DataType;

typedef struct {
    uint8_t opcode;
    uint32_t arg;
} Instruction;