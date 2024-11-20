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
        ds->data[address].type = UNASSIGNED_TYPE;
    }

    DataType data_type = ds->data[address].type;
    if (data_type != UNASSIGNED_TYPE && item.type != data_type)
        item.type = data_type;

    ds->data[address] = item;
}

void built_in_exit(VM *vm) { exit(EXIT_SUCCESS); }

void built_in_subprint(DataItem item, FILE *out) {
    if (item.type == INT_TYPE) {
        fprintf(out, "%d", (int)item.value);
    }
    else if (item.type == FLOAT_TYPE) {
        fprintf(out, "%g", extract_float(item));
    }
    else if (item.type == CHAR_TYPE) {
        fprintf(out, "%c", (char)item.value);
    }
}

void built_in_print(VM *vm) {
    DataItem element = pop(vm);

    if (element.type == ARRAY_TYPE) {
        DynamicArray arr = vm->array_storage[element.value];

        if (arr.type == CHAR_TYPE) {
            for (int i = 0; i < arr.size; i++)
            {
                DataItem item = {arr.type, arr.items[i]};
                built_in_subprint(item, stdout);
            }
        }
        else if (arr.type == ARRAY_TYPE) {
            printf("[");
            for (int i = 0; i < arr.size; i++)
            {
                DataItem item = {arr.type, arr.items[i]};
                push(vm, item);
                built_in_print(vm);
                if (i != arr.size - 1)
                    printf(", ");
            }
            printf("]");
        }
        else
        {
            printf("[");
            for (int i = 0; i < arr.size; i++)
            {
                DataItem item = {arr.type, arr.items[i]};
                built_in_subprint(item, stdout);
                if (i != arr.size - 1)
                    printf(", ");
            }
            printf("]");
        }
    }
    else
    {
        built_in_subprint(element, stdout);
    }
}

void built_in_input(VM *vm) {
    DataItem input = {INT_TYPE, 0};
    scanf("%d", &input.value);
    push(vm, input);
}

void built_in_getf(VM *vm) {
    float aux;
    scanf("%g", &aux);
    push(vm, (DataItem){FLOAT_TYPE, format_float(aux)});
}

void str_type(VM* vm, DynamicArray* arr, DataItem item) {
    char* get_type[ARRAY_TYPE + 1] = {
        "UNASSIGNED", "INT", "FLOAT",
        "CHAR", "ARRAY"
    };

    DataType type = item.type;

    for (int i = 0; get_type[type][i] != '\0'; i++)
        append_array(arr, get_type[type][i]);

    if (type == ARRAY_TYPE) {
        append_array(arr, 95);
        str_type(vm, arr, (DataItem){vm->array_storage[item.value].type, 0});
    }
} 

void built_in_type(VM *vm) {
    DataItem arg = pop(vm);
    DataItem type = {ARRAY_TYPE, vm->asp++};
    create_array(&vm->array_storage[type.value], 4);
    vm->array_storage[type.value].type = CHAR_TYPE;

    str_type(vm, &vm->array_storage[type.value], arg);
    push(vm, type);

}

void built_in_scan(VM *vm) {
    DataItem input = {ARRAY_TYPE, vm->asp++};
    char input_str[2048];

    scanf("%2047s", input_str);
    create_array(&vm->array_storage[input.value], 4);
    vm->array_storage[input.value].type = CHAR_TYPE;

    for (int i = 0; i < 2048 && input_str[i] != '\0'; i++)
        append_array(&vm->array_storage[input.value], input_str[i]);

    push(vm, input);
}

void built_in_read(VM *vm) {
    FILE *file;
    int start, end, binary;
    long file_length;
    end = pop(vm).value;
    binary = pop(vm).value;
    start = pop(vm).value;

    DynamicArray file_arr = vm->array_storage[pop(vm).value];
    DataItem read_result = {ARRAY_TYPE, vm->asp++};
    create_array(&vm->array_storage[read_result.value], 4);

    char filename[file_arr.size + 1];
    for (int i = 0; i < file_arr.size; i++)
        filename[i] = (char)file_arr.items[i];
    filename[file_arr.size] = '\0';

    file = fopen(filename, (binary) ? "rb" : "r");
    if (file == NULL)
        throw_error(error_messages[ERR_FILE_NOT_FOUND]);

    int i = start;
    fseek(file, 0, SEEK_END);
    file_length = ftell(file);
    if (binary > 0) {
        uint32_t aux;
        if (binary > 4)
            binary = 4;
        if (end < 0)
            end = file_length - (end + 1) * sizeof(uint8_t) * binary;
        fseek(file, start * sizeof(uint8_t) * binary, SEEK_SET);

        vm->array_storage[read_result.value].type = INT_TYPE;
        while (fread(&aux, sizeof(uint8_t) * binary, 1, file) && i < end) {
            append_array(&vm->array_storage[read_result.value], aux);
            i++;
        }
    }
    else
    {
        char c;
        if (end < 0)
            end = file_length - (end + 1);
        fseek(file, start, SEEK_SET);

        vm->array_storage[read_result.value].type = CHAR_TYPE;
        while ((c = fgetc(file)) != EOF && i < end) {
            append_array(&vm->array_storage[read_result.value], (uint32_t)((int)c));
            i++;
        }
    }

    push(vm, read_result);
    fclose(file);
}

void built_in_write(VM *vm) {
    FILE *file;
    DataItem to_write;
    int start, binary;
    long file_length;

    binary = pop(vm).value;
    to_write = pop(vm);
    start = pop(vm).value;
    DynamicArray file_arr = vm->array_storage[pop(vm).value];

    char filename[file_arr.size + 1];
    for (int i = 0; i < file_arr.size; i++)
        filename[i] = (char)file_arr.items[i];
    filename[file_arr.size] = '\0';

    if (binary == 0)
        file = fopen(filename, "r+");
    else if (binary == 1)
        file = fopen(filename, "r+b");
    else if (binary == 2)
        file = fopen(filename, "wb");
    else
    {
        file = fopen(filename, "w");
        binary = 0;
    }

    if (file == NULL)
        throw_error(error_messages[ERR_OPENING_FILE]);

    fseek(file, 0, SEEK_END);
    file_length = ftell(file);

    if (binary) {
        start *= sizeof(uint8_t);
        if (start < file_length)
            fseek(file, start, SEEK_SET);
        if (start < 0)
            fseek(file, (-1 * start) - 1, SEEK_END);

        if (to_write.type < ARRAY_TYPE) {
            fwrite(&to_write.value, sizeof(uint32_t), 1, file);
        }
        else
        {
            DynamicArray arr = vm->array_storage[to_write.value];
            for (int i = 0; i < arr.size; i++)
            {
                if (arr.type == CHAR_TYPE)
                    fwrite(&to_write.value, sizeof(uint8_t), 1, file);
                else if (arr.type < CHAR_TYPE)
                    fwrite(&to_write.value, sizeof(uint32_t), 1, file);
                else
                    throw_error(error_messages[ERR_WRITING_BINARY]);
            }
        }
    }
    else
    {
        if (start < file_length)
            fseek(file, start, SEEK_SET);
        if (start < 0)
            fseek(file, (-1 * start) - 1, SEEK_END);

        if (to_write.type < CHAR_TYPE) {
            built_in_subprint(to_write, file);
        }
        else
        {
            DynamicArray arr = vm->array_storage[to_write.value];
            for (int i = 0; i < arr.size; i++)
            {
                if (arr.type <= CHAR_TYPE)
                    built_in_subprint((DataItem){arr.type, arr.items[i]}, file);
                else
                    throw_error(error_messages[ERR_WRITING_FILE]);
            }
        }
    }

    fclose(file);
}

void (*builtins[])(VM *vm) = {
    built_in_exit,
    built_in_print,
    built_in_input,
    built_in_getf,
    built_in_type,
    built_in_scan,
    built_in_read,
    built_in_write,
};

void syscall(VM *vm, int arg) {
    if (arg > -1 && arg < 8)
        builtins[arg](vm);
    else
        printf("Unknown syscall: %d\n", arg);
}