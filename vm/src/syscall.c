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
        uint32_t data = item.value;
        for (int i = 0; i < 4; i++) {
            char ch = (data >> (8 * i)) & 0xFF;
            if (ch == '\0') break;
            fprintf(out, "%c", ch);
        }
    }
}

void built_in_print(VM *vm) {
    Item element = pop(&vm->stack);

    if (element.type == ARRAY_TYPE) {
        DataType arr_type = vm->heap.table_type[element.value];
        Memory arr = vm->heap.blocks[element.value];
        if (arr_type == CHAR_TYPE) {
            for (int i = 0; i < arr.size; i++) {
                Item item = { arr_type, arr.data[i] };
                built_in_subprint(item, stdout);
            }
        } else {
            printf("[");
            // for (int i = 0; i < arr.size; i++) {

            // }
            printf("]");
        }
        // printf("[");
        // for (int i = 0; i < arr.size; i++) {
        //     DataItem item = {arr.type, arr.items[i]};
        //     push(vm, item);
        //     built_in_print(vm);
        //     if (i != arr.size - 1)
        //         printf(", ");
        // }
        // printf("]");
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

// void str_type(VM* vm, DynamicArray* arr, DataItem item) {
//     char* get_type[ARRAY_TYPE + 1] = {
//         "UNASSIGNED", "INT", "FLOAT",
//         "CHAR", "ARRAY"
//     };

//     DataType type = item.type;

//     uint32_t temp = 0; int shift = 0;
//     for (int i = 0; get_type[type][i] != '\0'; i++) {
//         temp |= ((uint32_t)(unsigned char)get_type[type][i]) << shift;
//         shift += 8;

//         if (shift == 32) {
//             append_array(arr, temp);
//             temp = 0; shift = 0;
//         }
//     }

//     if (shift != 0) append_array(arr, temp);
//     if (type == ARRAY_TYPE) {
//         append_array(arr, 95);
//         str_type(vm, arr, (DataItem){vm->array_storage[item.value].type, 0});
//     }
// } 

void built_in_scan(VM *vm) {
    // DataItem input = {ARRAY_TYPE, vm->asp++};
    // char input_str[2048];

    // scanf("%2047s", input_str);
    // init_array(&vm->array_storage[input.value], 4);
    // vm->array_storage[input.value].type = CHAR_TYPE;

    // for (int i = 0; i < 2048 && input_str[i] != '\0'; i++)
    //     append_array(&vm->array_storage[input.value], input_str[i]);

    // push(vm, input);
}

void built_in_type(VM *vm) {
    // DataItem arg = pop(vm);
    // DataItem type = {ARRAY_TYPE, vm->asp++};
    // init_array(&vm->array_storage[type.value], 4);
    // vm->array_storage[type.value].type = CHAR_TYPE;

    // str_type(vm, &vm->array_storage[type.value], arg);
    // push(vm, type);
}

void built_in_read(VM *vm) {
    // FILE *file;
    // int start, end, binary;
    // long file_length;
    // end = pop(vm).value;
    // binary = pop(vm).value;
    // start = pop(vm).value;

    // DynamicArray file_arr = vm->array_storage[pop(vm).value];
    // DataItem read_result = {ARRAY_TYPE, vm->asp++};
    // init_array(&vm->array_storage[read_result.value], 4);

    // int index = 0;
    // char filename[file_arr.size * 4 + 1];
    // for (int i = 0; i < file_arr.size; i++)
    //     for (int j = 0; j < 4; j++)
    //         filename[index++] = (file_arr.items[i] >> (8 * j)) & 0xFF;
    
    // filename[file_arr.size * 4] = '\0';

    // file = fopen(filename, (binary) ? "rb" : "r");
    // if (file == NULL) throw_error(error_messages[ERR_FILE_NOT_FOUND]);

    // int i = start;
    // fseek(file, 0, SEEK_END);
    // file_length = ftell(file);
    // if (binary > 0) {
    //     uint32_t aux;
    //     if (binary > 4) binary = 4;
    //     if (end < 0) end = file_length - (end + 1) * sizeof(uint8_t) * binary;
    //     fseek(file, start * sizeof(uint8_t) * binary, SEEK_SET);

    //     vm->array_storage[read_result.value].type = UNASSIGNED_TYPE;
    //     while (fread(&aux, sizeof(uint8_t) * binary, 1, file) && i < end) {
    //         append_array(&vm->array_storage[read_result.value], aux);
    //         i++;
    //     }
    // } else {
    //     char c;
    //     if (end < 0) end = file_length - (end + 1);
    //     fseek(file, start, SEEK_SET);

    //     vm->array_storage[read_result.value].type = CHAR_TYPE;
    //     int shift = 0; uint32_t temp = 0;
    //     while ((c = fgetc(file)) != EOF && i < end) {
    //         temp |= ((uint32_t)(unsigned char)c) << shift;
    //         shift += 8; i++;

    //         if (shift == 32 || i == end) {
    //             append_array(&vm->array_storage[read_result.value], temp);
    //             temp = 0; shift = 0;
    //         }
    //     }

    //     if (shift != 0) append_array(&vm->array_storage[read_result.value], temp);
    // }

    // push(vm, read_result);
    // fclose(file);
}

void built_in_write(VM *vm) {
    // FILE *file;
    // DataItem to_write;
    // int start, binary, overwrite;
    // long file_length;

    // overwrite = pop(vm).value;
    // binary = pop(vm).value;
    // to_write = pop(vm);
    // DynamicArray file_arr = vm->array_storage[pop(vm).value];

    // int index = 0;
    // char filename[file_arr.size * 4 + 1];
    // for (int i = 0; i < file_arr.size; i++)
    //     for (int j = 0; j < 4; j++)
    //         filename[index++] = (file_arr.items[i] >> (8 * j)) & 0xFF;
    
    // filename[file_arr.size * 4] = '\0';

    // file = fopen(filename, (overwrite) ? "w+" : "ab+");

    // if (file == NULL)
    //     throw_error(error_messages[ERR_OPENING_FILE]);

    // fseek(file, 0, SEEK_END);
    // file_length = ftell(file);

    // if (binary) {
    //     if (to_write.type < ARRAY_TYPE) {
    //         fwrite(&to_write.value, sizeof(uint32_t), 1, file);
    //     } else {
    //         DynamicArray arr = vm->array_storage[to_write.value];
    //         for (int i = 0; i < arr.size; i++) {
    //             uint32_t to_write_value = vm->array_storage[to_write.value].items[i];
    //             if (arr.type == CHAR_TYPE) fwrite(&to_write_value, sizeof(uint8_t), 1, file);
    //             else if (arr.type < CHAR_TYPE) fwrite(&to_write_value, sizeof(uint32_t), 1, file);
    //             else throw_error(error_messages[ERR_WRITING_BINARY]);
    //         }
    //     }
    // } else {
    //     if (to_write.type < CHAR_TYPE) {
    //         built_in_subprint(to_write, file);
    //     } else {
    //         DynamicArray arr = vm->array_storage[to_write.value];
    //         for (int i = 0; i < arr.size; i++) {
    //             if (arr.type <= CHAR_TYPE) built_in_subprint((DataItem){arr.type, arr.items[i]}, file);
    //             else throw_error(error_messages[ERR_WRITING_FILE]);
    //         }
    //     }
    // }

    // fclose(file);
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
    if (arg > -1 && arg < 8) builtins[arg](vm);
    else printf("Unknown syscall: %d\n", arg);
}