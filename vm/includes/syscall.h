#include "../virtual_machine.h"

#include "alu.h"
#include "errors.h"
#include "stack.h"
#include "strucs-type.h"

#include <stdlib.h>
#include <stdio.h>
#include <math.h>

void built_in_exit(VM *vm);
void built_in_subprint(Item item, FILE *out);
void built_in_print(VM *vm);
void built_in_input(VM *vm);
void built_in_getf(VM *vm);
// void str_type(VM* vm, DynamicArray* arr, DataItem item);
void built_in_scan(VM *vm);
void built_in_type(VM *vm);
void built_in_read(VM *vm);
void built_in_write(VM *vm);
void syscall(VM *vm, int arg);