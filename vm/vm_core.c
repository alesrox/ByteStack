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

void built_in_exit(VM* vm) { exit(EXIT_SUCCESS); }

void built_in_subprint(DataItem item) {
    if (item.type == INT_TYPE) {
        printf("%d", (int) item.value);
    } else if (item.type == FLOAT_TYPE) {
        printf("%g", extract_float(item));
    } else if (item.type == CHAR_TYPE) {
        printf("%c", (char) item.value);
    }
}

void built_in_print(VM* vm) {
    DataItem element = pop(vm);

    if (element.type == ARRAY_TYPE) {
        DynamicArray arr = vm->array_storage[element.value];

        if (arr.type == CHAR_TYPE) {
            for (int i = 0; i < arr.size; i++) {
                DataItem item = {arr.type, arr.items[i]};
                built_in_subprint(item);
            }
        } else if (arr.type == ARRAY_TYPE){
            printf("[");
            for (int i = 0; i < arr.size; i++) {
                DataItem item = {arr.type, arr.items[i]};
                push(vm, item);
                built_in_print(vm);
                if (i != arr.size -1) printf(", ");
            }
            printf("]");
        } else {
            printf("[");
            for (int i = 0; i < arr.size; i++) {
                DataItem item = {arr.type, arr.items[i]};
                built_in_subprint(item);
                if (i != arr.size -1) printf(", ");
            }
            printf("]");
        }
    } else {
        built_in_subprint(element);
    }
}

void built_in_input(VM* vm) {
    DataItem input = {INT_TYPE, 0};
    scanf("%d", &input.value);
    push(vm, input);
}

void built_in_getf(VM* vm) {
    float aux;
    scanf("%g", &aux);
    push(vm, (DataItem){FLOAT_TYPE, format_float(aux)});
}

void built_in_scan(VM* vm) {
    DataItem input = {ARRAY_TYPE, vm->asp++};
    char input_str[2048];

    scanf("%2047s", input_str);
    create_array(&vm->array_storage[input.value], 4);
    vm->array_storage[input.value].type = CHAR_TYPE;
    
    for (int i = 0; i < 2048 && input_str[i] != '\0'; i++) {
        append_array(&vm->array_storage[input.value], input_str[i]);
    }

    push(vm, input);
}

void (*builtins[])(VM* vm) = {
    built_in_exit,
    built_in_print,
    built_in_input,
    built_in_getf,
    built_in_scan,
};

void syscall(VM *vm, int arg) {
    if (arg > -1 && arg < 5) builtins[arg](vm);
    else printf("Unknown syscall: %d\n", arg);
}