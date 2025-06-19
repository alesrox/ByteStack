#pragma once
#include "structs-type.h"
#include "errors.h"

#define STACK_SIZE 1024
int string_format;

// Method: Tagged Struct - To see later: NaN-Boxing
typedef struct {
    DataType type;
    uint32_t value;
} Item;

typedef struct {
    Item data[STACK_SIZE];
    int top;
} Stack;

void stack_init(Stack*);
void print_stack(const Stack);
void push(Stack*, Item);
Item pop(Stack*);
