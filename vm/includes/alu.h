#pragma once
#include "strucs-type.h"
#include "stack.h"
#include <math.h>

void alu(Stack*, uint8_t);
Item logic_unit(Stack*, uint8_t);
Item aritmetic_unit(Stack*, uint8_t);

float float_alu(Item, Item, uint8_t);
uint32_t format_float(float);
uint32_t int_alu(Item, Item, uint8_t);

float extract_float(Item);
float float_mod(float, float);