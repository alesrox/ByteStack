#include "../includes/syscall.h"

void built_in_exit(VM *vm) { exit(EXIT_SUCCESS); }

void built_in_subprint(Item item, FILE *out) {
    if (item.type == INT_TYPE) {
        fprintf(out, "%d", (int) item.value);
    } else if (item.type == BOOL_TYPE) {
        if (item.value == 1)
            fprintf(out, "True");
        else if (item.value == 0)
            fprintf(out, "False");
        else
            fprintf(out, "%d", (int8_t) item.value);
    } else if (item.type == FLOAT_TYPE) {
        fprintf(out, "%g", extract_float(item));
    } else if (item.type == CHAR_TYPE) {
        fprintf(out, "%c", item.value);
    }
}

void built_in_print(VM *vm) {
    Item element = pop(&vm->stack);

    if (element.type == ARRAY_TYPE) {
        Item item;
        Memory arr = vm->heap.blocks[element.value];
        DataType arr_type = vm->heap.table_type[element.value];
        
        if (arr_type == CHAR_TYPE) {
            for (int i = 0; i < arr.size; i++) {
                item = (Item){ arr_type, arr.data[i] };
                built_in_subprint(item, stdout);
            }
        } else {
            printf("[");
            for (int i = 0; i < arr.size/sizes[arr_type]; i++) {
                uint32_t value;
                heap_read(&vm->heap, element.value, &value, i * sizes[arr_type], sizes[arr_type]);
                item = (Item){ arr_type, value }; 
                push(&vm->stack, item);
                built_in_print(vm);
                if (i != arr.size/sizes[arr_type] - 1) printf(", ");
            }
            printf("]");
        }
    } else {
        built_in_subprint(element, stdout);
    }
}

void built_in_input(VM *vm) {
    Item input = {INT_TYPE, 0};
    scanf("%d", &input.value);
    push(&vm->stack, input);
}

void built_in_getf(VM *vm) {
    float aux;
    scanf("%g", &aux);
    push(&vm->stack, (Item){FLOAT_TYPE, format_float(aux)});
}

void built_in_scan(VM *vm) {
    char input_str[2048];
    scanf("%2047s", input_str);

    size_t address = heap_add_block(&vm->heap, CHAR_TYPE);
    for (int i = 0; i < 2048 && input_str[i] != '\0'; i++)
        heap_write(&vm->heap, address, input_str[i], i, 1);
    
    push(&vm->stack, (Item) {
        ARRAY_TYPE,
        address
    });
}

void built_in_type(VM *vm) {
    DataType arg_type = pop(&vm->stack).type;
    size_t address = heap_add_block(&vm->heap, CHAR_TYPE);

    char* get_type[ARRAY_TYPE + 1] = {
        "UNASSIGNED", "BYTE", "INT", "FLOAT",
        "CHAR", "ARRAY"
    };

    for (int i = 0; get_type[arg_type][i] != '\0'; i++)
        heap_write(&vm->heap, address, get_type[arg_type][i], i, 1);

    push(&vm->stack, (Item) {
        ARRAY_TYPE,
        address
    });
}

void built_in_read(VM *vm) {
    FILE *file;
    int from, bytes_to_read;

    uint32_t filename_address = pop(&vm->stack).value;
    int length = vm->heap.blocks[filename_address].size;

    char filename[length + 1];
    for (int i = 0; i < length; i++) {
        uint32_t aux;
        heap_read(&vm->heap, filename_address, &aux, i, 1);
        filename[i] = (char) aux;
    }
    filename[length] = '\0';
    file = fopen(filename, "rb");
    if (file == NULL) handle_error(FILE_NOT_FOUND);

    from = pop(&vm->stack).value;
    bytes_to_read = pop(&vm->stack).value;

    uint8_t aux;
    fseek(file, 0, SEEK_END);
    int file_length = ftell(file);
    if (from < 0) from = file_length - (from + 1);
    fseek(file, from, SEEK_SET);

    int read_pointer = from;
    int address = heap_add_block(&vm->heap, BOOL_TYPE);
    while (fread(&aux, 1, 1, file) && read_pointer < from + bytes_to_read) {
        heap_write(&vm->heap, address, aux, read_pointer - from, 1);
        read_pointer++;
    }

    fclose(file);
    push(&vm->stack, (Item) {
        ARRAY_TYPE,
        address
    });
}

void built_in_write(VM *vm) {
    FILE *file;
    uint32_t filename_address, value_address;
    uint32_t bytes_to_write, overwrite;

    filename_address = pop(&vm->stack).value;
    int length = vm->heap.blocks[filename_address].size;

    char filename[length + 1];
    for (int i = 0; i < length; i++) {
        uint32_t aux;
        heap_read(&vm->heap, filename_address, &aux, i, 1);
        filename[i] = (char) aux;
    }

    value_address = pop(&vm->stack).value;
    bytes_to_write = pop(&vm->stack).value;
    overwrite = pop(&vm->stack).value;

    filename[length] = '\0';
    file = fopen(filename, (overwrite != (uint32_t) 0) ? "wb" : "ab");
    if (file == NULL) handle_error(FILE_NOT_FOUND);

    size_t i;
    uint8_t buffer; uint32_t buffer4;
    for (i = 0; i < bytes_to_write; i++) {
        heap_read(&vm->heap, value_address, &buffer4, i, 1);
        buffer = (uint8_t) buffer4;
        fwrite(&buffer, 1, 1, file);
    }

    push(&vm->stack, (Item) {
        INT_TYPE,
        i
    });
}

void built_in_size(VM* vm) {
    Item arr = pop(&vm->stack);
    push(&vm->stack, (Item) {
        INT_TYPE,
        vm->heap.blocks[arr.value].size
    });
}

void built_in_append(VM* vm) {
    Item arr, item;
    arr = pop(&vm->stack);
    item = pop(&vm->stack);
    if (item.type != vm->heap.table_type[arr.value]) handle_error(UNDEFINED_ERROR);

    heap_write(&vm->heap, arr.value, item.value, vm->heap.blocks[arr.value].size, sizes[arr.type]);
}

// TODO: Para implementar
void built_in_remove_at(VM* vm) {
    Item arr, index;
    arr = pop(&vm->stack); index = pop(&vm->stack);

    if (index.value < 0 || index.value > vm->heap.blocks[arr.value].size)
        handle_error(INDEX_OUT_OF_BOUNDS);
    
    DataType arr_type = vm->heap.table_type[arr.value];
    heap_remove_element(&vm->heap, arr.value, index.value, sizes[arr_type]);
}

void built_in_is_empty(VM* vm) {
    Item arr = pop(&vm->stack);
    
    Item result = {
        BOOL_TYPE,
        (vm->heap.blocks[arr.value].size == 0) ? 1 : 0
    };

    push(&vm->stack, result);
}

void built_in_slice(VM* vm) {
    
}

// TODO: 
void built_in_map(VM* vm) {
    Item arr, func_dir;
    arr = pop(&vm->stack); func_dir = pop(&vm->stack);

    push(&vm->stack, arr);
}

void built_in_filter(VM* vm) {
    Item arr, func_dir;
    arr = pop(&vm->stack); func_dir = pop(&vm->stack);

    push(&vm->stack, arr);
}

void built_in_min(VM* vm) {
    Item arr = pop(&vm->stack);
    size_t block_index = arr.value;
    DataType arr_type = vm->heap.table_type[block_index];
    Memory* block = &vm->heap.blocks[block_index];

    size_t elem_size = sizes[arr_type];
    size_t total_elems = block->size / elem_size;

    uint32_t min_value;
    heap_read(&vm->heap, block_index, &min_value, 0, elem_size);

    for (size_t i = 1; i < total_elems; i++) {
        uint32_t buffer;
        heap_read(&vm->heap, block_index, &buffer, i * elem_size, elem_size);

        if (arr_type == FLOAT_TYPE) {
            float current = extract_float((Item){FLOAT_TYPE, buffer});
            float current_min = extract_float((Item){FLOAT_TYPE, min_value});
            if (current < current_min) {
                min_value = buffer;
            }
        } else {
            if (buffer < min_value) {
                min_value = buffer;
            }
        }
    }

    push(&vm->stack, (Item){arr_type, min_value});
}

void built_in_max(VM* vm) {
    Item arr = pop(&vm->stack);
    size_t block_index = arr.value;
    DataType arr_type = vm->heap.table_type[block_index];
    Memory* block = &vm->heap.blocks[block_index];

    size_t elem_size = sizes[arr_type];
    size_t total_elems = block->size / elem_size;

    uint32_t max_value;
    heap_read(&vm->heap, block_index, &max_value, 0, elem_size);

    for (size_t i = 1; i < total_elems; i++) {
        uint32_t buffer;
        heap_read(&vm->heap, block_index, &buffer, i * elem_size, elem_size);

        if (arr_type == FLOAT_TYPE) {
            float current = extract_float((Item){FLOAT_TYPE, buffer});
            float current_min = extract_float((Item){FLOAT_TYPE, max_value});
            if (current > current_min) {
                max_value = buffer;
            }
        } else {
            if (buffer > max_value) {
                max_value = buffer;
            }
        }
    }

    push(&vm->stack, (Item){arr_type, max_value});
}

// TODO:
void built_in_lower(VM* vm) {}
void built_in_upper(VM* vm) {}

void built_in_toString(VM* vm) {}

void (*builtins[])(VM *vm) = {
    built_in_exit,
    built_in_print,
    built_in_input,
    built_in_getf,
    built_in_scan,
    built_in_type,
    built_in_read,
    built_in_write,
    built_in_size,
    built_in_append,
    built_in_remove_at,
    built_in_is_empty,
    built_in_map,
    built_in_slice,
    built_in_filter,
    built_in_min,
    built_in_max,
    built_in_lower,
    built_in_upper,
    built_in_toString,
};

void syscall(VM *vm, int arg) {
    if (arg > -1 && arg < 20) builtins[arg](vm);
    else printf("Unknown syscall: %d\n", arg);
}