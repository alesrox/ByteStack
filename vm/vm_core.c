#include "virtual_machine.h"

void push(VM *vm, DataItem value) {
    if (vm->sp < STACK_SIZE)
        vm->stack[vm->sp++] = value;
}

DataItem pop(VM *vm) {
    if (vm->sp == 0)
        throw_error(error_messages[ERR_EMPTY_STACK]);

    return vm->stack[--vm->sp];
}

void store_data(VM *vm, int address, DataItem item) {
    if (address == -1) address = vm->mp;
    if (address >= 0 && address < MEMORY_SIZE) {
        vm->data_memory[address].type = item.type;
        vm->data_memory[address].value = item.value;
        vm->mp++;
    } else {
        throw_error(error_messages[ERR_MEMORY_OUT_OF_BOUNDS]);
    }
}

DataItem load_data(VM *vm, int address) {
    if (address < 0 || address > MEMORY_SIZE)
        throw_error(error_messages[ERR_MEMORY_OUT_OF_BOUNDS]);

    return vm->data_memory[address];
}

void syscall(VM *vm, int arg) {
    DataItem element, aux;
    switch (arg) {
        case 0: // exit
            exit(EXIT_SUCCESS);
            break;

        case 1: // print
            element = pop(vm);
            if (element.type == INT_TYPE) {
                printf("%d\n", element.value);
            } else if (element.type == FLOAT_TYPE) {
                printf("%g\n", extract_float(element));
            } else if (element.type == ARRAY_TYPE) {
                DynamicArray arr = vm->array_storage[element.value];
                for (int i = 0; i < arr.size; i++) {
                    printf("%d, ", arr.items[i]);
                }
            }
            break;

        case 2: // input
            element.type = INT_TYPE;
            scanf("%d", &element.value);
            push(vm, element);
            break;

        case 3: // (list).append
            element = pop(vm);
            aux = pop(vm);
            if (vm->array_storage[element.value].type != aux.type)
                throw_error(error_messages[ERR_BAD_TYPE_ARR]);

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