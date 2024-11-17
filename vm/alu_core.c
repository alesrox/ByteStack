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
    switch (op) {
        case 0x01: // ADD
            return extract_float(left) + extract_float(right);
        case 0x02: // SUB
            return extract_float(left) - extract_float(right);
        case 0x03: // MUL
            return extract_float(left) * extract_float(right);
        case 0x04: // DIV
            return extract_float(left) / extract_float(right);
        case 0x05: // MOD
            return float_mod(extract_float(left), extract_float(right));
        case 0x09: // EQ
            return extract_float(left) == extract_float(right);
        case 0x0A: // NEQ
            return extract_float(left) != extract_float(right);
        case 0x0B: // LT
            return extract_float(left) < extract_float(right);
        case 0x0C: // GT
            return extract_float(left) > extract_float(right);
        case 0x0D: // LE
            return extract_float(left) <= extract_float(right);
        case 0x0E: // GE
            return extract_float(left) >= extract_float(right);
    }
}

int int_alu(VM* vm, uint32_t left, uint32_t right, uint8_t op) {
    switch (op) {
        case 0x01: // ADD
            return left + right;
        case 0x02: // SUB
            return left - right;
        case 0x03: // MUL
            return left * right;
        case 0x04: // DIV
            return left / right;
        case 0x05: // MOD
            return left % right;
        case 0x09: // EQ
            return left == right;
        case 0x0A: // NEQ
            return left != right;
        case 0x0B: // LT
            return left < right;
        case 0x0C: // GT
            return left > right;
        case 0x0D: // LE
            return left <= right;
        case 0x0E: // GE
            return left >= right;
    }
}

DataItem alu(VM* vm, DataItem left, DataItem right, uint8_t op) {
    // Only integers, floats and booleans
    DataItem result;
    result.type = INT_TYPE;

    if (op >= 0x06 && op <= 0x08) {
        result.value = (vm, left.value, right.value, op);
    } else if (left.type == FLOAT_TYPE || right.type == FLOAT_TYPE) {
        result.type = FLOAT_TYPE;
        result.value = format_float(float_alu(vm, left, right, op));
    } else {
        result.value = int_alu(vm, left.value, right.value, op);
    }

    return result;
}