#include "../includes/alu.h"

void alu(Stack *stack, uint8_t op) {
    Item result;

    int logic_op = op >= 0x06 && op <= 0x08;
    if (logic_op) {
        result = logic_unit(stack, op);
    } else {
        result = aritmetic_unit(stack, op);
    }

    push(stack, result);
}

Item logic_unit(Stack *stack, uint8_t op) {
    Item left, right;
    right = pop(stack);
    
    if (op == 0x08) // NOT OPERATOR
        return (Item) { BOOL_TYPE, !right.value };
    
    left = pop(stack);
    uint32_t value = (op == 0x06) ? // AND or OR OPERATORS
        (left.value && right.value) : (left.value || right.value);

    return (Item) { BOOL_TYPE, value };
}

Item aritmetic_unit(Stack *stack, uint8_t op) {
    Item result, left, right;
    right = pop(stack); left = pop(stack);
    int requires_float = left.type == FLOAT_TYPE || right.type == FLOAT_TYPE;
    int div_mod_op = op == 0x04 || op == 0x05;

    if (requires_float || div_mod_op)
        return (Item) {
            FLOAT_TYPE,
            format_float(float_alu(left, right, op))
        };
    
    return (Item) {
        INT_TYPE,
        int_alu(left, right, op)
    };
}

float float_alu(Item left, Item right, uint8_t op) {
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

uint32_t int_alu(Item left, Item right, uint8_t op) {
    switch (op) {
        case 0x01: // ADD
            return left.value + right.value;
        case 0x02: // SUB
            return left.value - right.value;
        case 0x03: // MUL
            return left.value * right.value;
        case 0x09: // EQ
            return left.value == right.value;
        case 0x0A: // NEQ
            return left.value != right.value;
        case 0x0B: // LT
            return (int) left.value < (int) right.value;
        case 0x0C: // GT
            return (int) left.value > (int) right.value;
        case 0x0D: // LE
            return (int) left.value <= (int) right.value;
        case 0x0E: // GE
            return (int) left.value >= (int) right.value;
    }

    return 0;
}

uint32_t format_float(float value) {
    return *((uint32_t*) &(value));
}

float extract_float(Item item) {
    if (item.type == FLOAT_TYPE){
        return *((float*)&item.value);}

    return (float) ((int) item.value);
}

float float_mod(float a, float b) {
    return a - b * floorf(a / b);
}