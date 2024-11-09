#include "virtual_machine.h"
#include <math.h>

void push(VM *vm, DataItem value) {
    if (vm->sp < STACK_SIZE)
        vm->stack[vm->sp++] = value;
}

DataItem pop(VM *vm) {
    if (vm->sp == 0)
        throw_error(error_messages[ERR_EMPTY_STACK]);

    return vm->stack[--vm->sp];
}

void store_data(DataSegment *ds, int address, DataItem item) {
    if (address == -1) {
        address = ds->pointer;
        ds->pointer++;
        if (address >= ds->capacity) {
            ds->capacity *= 2;
            ds->data = realloc(ds->data, ds->capacity * sizeof(DataItem));
        }
    }

    ds->data[address] = item;
}

void sub_print(DataItem item) {
    if (item.type == INT_TYPE) {
        printf("%d", (int) item.value);
    } else if (item.type == FLOAT_TYPE) {
        printf("%g", extract_float(item));
    } else if (item.type == CHAR_TYPE) {
        printf("%c", (char) item.value);
    }
}

void sup_print(VM* vm, DataItem element) {
    if (element.type == ARRAY_TYPE) {
        DynamicArray arr = vm->array_storage[element.value];

        if (arr.type == CHAR_TYPE) {
            for (int i = 0; i < arr.size; i++) {
                DataItem item = {arr.type, arr.items[i]};
                sub_print(item);
            }
        } else if (arr.type == ARRAY_TYPE){
            printf("[");
            for (int i = 0; i < arr.size; i++) {
                DataItem item = {arr.type, arr.items[i]};
                //printf("%d - %d", arr.type, arr.items[i]);
                sup_print(vm, item);
                if (i != arr.size -1) printf(", ");
            }
            printf("]");
        } else {
            printf("[");
            for (int i = 0; i < arr.size; i++) {
                DataItem item = {arr.type, arr.items[i]};
                sub_print(item);
                if (i != arr.size -1) printf(", ");
            }
            printf("]");
        }
    } else {
        sub_print(element);
    }
}

void syscall(VM *vm, int arg) {
    DataItem element, aux;
    switch (arg) {
        case 0: // exit
            exit(EXIT_SUCCESS);
            break;

        case 1: // print
            element = pop(vm);
            sup_print(vm, element);
            break;

        case 2: // input
            element.type = INT_TYPE;
            scanf("%d", &element.value);
            push(vm, element);
            break;

        case 3: // (list).append
            element = pop(vm);
            aux = pop(vm);
            if (vm->array_storage[element.value].type != aux.type) {
                throw_error(error_messages[ERR_BAD_TYPE_ARR]);
            }

            append_array(&vm->array_storage[element.value], aux.value);
            break;
        
        case 4: // (list).size
            element = pop(vm);
            aux.type = INT_TYPE;
            aux.value = vm->array_storage[element.value].size;
            push(vm,aux);
            break;
    }
}