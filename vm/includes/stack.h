#pragma once
#include "strucs-type.h"
#include "errors.h"

#define STACK_SIZE 1024

// Method: Tagged Struct - To see later: NaN-Boxing
typedef struct {
    DataType type;
    uint32_t value;
} Item;

typedef struct {
    Item data[STACK_SIZE];
    int top;
} Stack;

void stack_init(Stack *stack);
void print_stack(const Stack stack);
void push(Stack *stack, Item value);
Item pop(Stack *stack);
