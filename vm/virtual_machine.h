#pragma once
#include "includes/memory.h"
#include "includes/stack.h"
#include "includes/errors.h"
#include "stdio.h"
#define RECURSION_LIMIT 128

typedef struct {
    int program_size;
    int frame_pointer;
    
    Stack stack;
    Memory memory;
    Heap heap;

    Instruction *pc;
    Instruction *bytecode;
    Instruction* return_address[RECURSION_LIMIT];
} VM;

void vm_init(VM *vm, const char *filename);
void vm_destroy(VM *vm);
void vm_run(VM *vm);