#include <math.h>
#include "virtual_machine.h"

uint32_t format_float(float value) {
    return *((uint32_t*) &(value));
}

float extract_float(DataItem item) {
    if (item.type == FLOAT_TYPE){
        return *((float*)&item.value);}

    return (float) ((int) item.value);
}

float float_mod(float a, float b) {
    return a - b * floorf(a / b);
}

int logic_unit(VM* vm, uint32_t left, uint32_t right, uint8_t op) {
    DataItem result;
    result.type = INT_TYPE;

    return  (op == 0x06) ? (left && right) :  // AND
            (op == 0x07) ? (left || right) :  // OR
            !left;
}

float float_alu(VM* vm, DataItem left, DataItem right, uint8_t op) {
    float left_float = extract_float(left);
    float right_float = extract_float(right);

    switch (op) {
        case 0x01: // ADD
            return left_float + right_float;
        case 0x02: // SUB
            return left_float - right_float;
        case 0x03: // MUL
            return left_float * right_float;
        case 0x04: // DIV
            return left_float / right_float;
        case 0x05: // MOD
            return float_mod(left_float, right_float);
        case 0x09: // EQ
            return left_float == right_float;
        case 0x0A: // NEQ
            return left_float != right_float;
        case 0x0B: // LT
            return left_float < right_float;
        case 0x0C: // GT
            return left_float > right_float;
        case 0x0D: // LE
            return left_float <= right_float;
        case 0x0E: // GE
            return left_float >= right_float;
    }

    return 0;
}

uint32_t int_alu(VM* vm, uint32_t left, uint32_t right, uint8_t op) {
    switch (op) {
        case 0x01: // ADD
            return left + right;
        case 0x02: // SUB
            return left - right;
        case 0x03: // MUL
            return left * right;
        case 0x09: // EQ
            return left == right;
        case 0x0A: // NEQ
            return left != right;
        case 0x0B: // LT
            return (int) left < (int) right;
        case 0x0C: // GT
            return (int) left > (int) right;
        case 0x0D: // LE
            return (int) left <= (int) right;
        case 0x0E: // GE
            return (int) left >= (int) right;
    }

    return 0;
}

DataItem alu(VM* vm, DataItem left, DataItem right, uint8_t op) {
    // Only integers, floats and booleans
    DataItem result;
    result.type = INT_TYPE;

    int logic_op = op >= 0x06 && op <= 0x08;
    int requires_float = left.type == FLOAT_TYPE || right.type == FLOAT_TYPE;
    int div_mod_op = op == 0x04 || op == 0x05;

    if (logic_op) {
        result.value = logic_unit(vm, left.value, right.value, op);
    } else if (requires_float || div_mod_op) {
        result.type = FLOAT_TYPE;
        result.value = format_float(float_alu(vm, left, right, op));
    } else {
        result.value = int_alu(vm, left.value, right.value, op);
    }

    return result;
}