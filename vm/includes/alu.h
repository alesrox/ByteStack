#pragma once
#include "strucs-type.h"
#include "stack.h"
#include <math.h>

void alu(Stack *stack, uint8_t op);
Item logic_unit(Stack *stack, uint8_t op);
Item aritmetic_unit(Stack *stack, uint8_t op);

float float_alu(Item left, Item right, uint8_t op);
uint32_t format_float(float value);
uint32_t int_alu(Item left, Item right, uint8_t op);

float extract_float(Item item);
float float_mod(float a, float b);