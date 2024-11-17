#include "virtual_machine.h"

const int STORE_FLOAT_CODE = 0x10;
char* error_messages[ERR_COUNT] = {
    "Error: Binary file not found",
    "Error: Maximum recursion depth exceeded",
    "Error: Memory access out of bounds",
    "Error: Attempted to access an empty stack",
    "Error: Tried to store incorrect type on a array",
    "Error: Index out of bounds",
};

void throw_error(char* msg) {
    printf("\nExecution error: %s", msg);
    exit(EXIT_FAILURE);
}

int load_program(VM *vm, const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (!file) throw_error(error_messages[ERR_FILE_NOT_FOUND]);
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    int num_instructions = size/5;

    vm->data_segment.pointer = 0;
    vm->data_segment.capacity = MEMORY_SIZE;
    vm->data_segment.data = malloc(sizeof(DataItem) * vm->data_segment.capacity);
    vm->memory = malloc(sizeof(Instruction) * num_instructions);

    for (int i = 0; i < num_instructions; i++) {
        fread(&vm->memory[i].opcode, sizeof(uint8_t), 1, file);
        vm->memory[i].arg.type = (vm->memory[i].opcode == STORE_FLOAT_CODE) ? FLOAT_TYPE : INT_TYPE; 
        fread(&vm->memory[i].arg.value, sizeof(uint32_t), 1, file);
    }

    fclose(file);

    vm->pc = 0;
    vm->sp = 0;
    vm->fp = 0;
    vm->asp = 0;

    return num_instructions;
}

void run(VM *vm, int size) {
    do {
        Instruction instr = vm->memory[vm->pc++];
        DataItem left, right, result;
        int address, index, array_access, aux, length;

        // printf("0x%02X - %d\n", instr.opcode, instr.arg.value);
        if (instr.opcode < 0x0F) {
            right = (instr.opcode != 0x08) ? pop(vm) : (DataItem){0, 0};
            left = pop(vm);

            // Only ints or floats
            if (right.type + left.type <= 2) {
                result = alu(vm, left, right, instr.opcode);
                push(vm, result);
                continue;
            } 
        }

        switch (instr.opcode) {
            case 0x01: // ADD -> Only if some of one are an array -> WILL BE MODIFIED
                if (right.type == ARRAY_TYPE && left.type == ARRAY_TYPE) {
                    DynamicArray arr = vm->array_storage[right.value];
                    if (vm->array_storage[left.value].type == CHAR_TYPE && arr.type != CHAR_TYPE) {
                        convert_list_to_str(vm, &vm->array_storage[left.value], arr);
                    } else {
                        for (int i = 0; i < arr.size; i++)
                            append_array(&vm->array_storage[left.value], arr.items[i]);
                    }

                    result = left;
                } else /*if (right.type == ARRAY_TYPE ^ left.type == ARRAY_TYPE)*/ {
                    DynamicArray* arr = &vm->array_storage[(right.type == ARRAY_TYPE) ? right.value : left.value];
                    DataItem item = (right.type != ARRAY_TYPE) ? right : left;

                    void (*convert_func)(DynamicArray*, uint32_t);
                    convert_func = (item.type == INT_TYPE) ? convert_int_to_str : convert_float_to_str;

                    if (arr->type == CHAR_TYPE) convert_func(arr, item.value);
                    else append_array(arr, item.value);

                    result = (right.type == ARRAY_TYPE) ? right : left;
                }

                push(vm, result);
                break;

            case 0x0F: // STORE
                push(vm, instr.arg);
                break;

            case 0x10: // STORE_FLOAT
                push(vm, instr.arg);
                break;

            case 0x11: // STORE_MEM
                store_data(&vm->data_segment, instr.arg.value, pop(vm));
                break;

            case 0x12: // LOAD
                push(vm, vm->data_segment.data[instr.arg.value]);
                break;

            case 0x13: // JUMP
                vm->pc = instr.arg.value;
                break;

            case 0x14: // JUMP_IF
                if (pop(vm).value) 
                    vm->pc = instr.arg.value;
                break;
            
            case 0x15: // CREATE_SCOPE
                if (vm->fp >= RECURSION_LIMIT) throw_error(error_messages[ERR_RECURSION_LIMIT]);

                vm->frames[vm->fp].locals.pointer = 0;
                vm->frames[vm->fp].locals.capacity = MEMORY_SIZE;
                vm->frames[vm->fp].locals.data = malloc(sizeof(DataItem) * vm->frames[vm->fp].locals.capacity);
                vm->fp++;
                break;
            
            case 0x16: // DEL_SCOPE
                free(vm->frames[vm->fp--].locals.data);
                break;

            case 0x17: // CALL
                if (vm->fp == RECURSION_LIMIT) throw_error(error_messages[ERR_RECURSION_LIMIT]);

                vm->frames[vm->fp].locals.pointer = 0;
                vm->frames[vm->fp].locals.capacity = MEMORY_SIZE;
                vm->frames[vm->fp].locals.data = malloc(sizeof(DataItem) * MEMORY_SIZE);
                vm->frames[vm->fp].return_address = vm->pc;
                vm->pc = instr.arg.value;
                vm->fp++;
                break;

            case 0x18: // STORE_LOCAL
                left = pop(vm);
                store_data(&vm->frames[vm->fp - 1].locals, instr.arg.value, left);
                break;
            
            case 0x19: // LOAD_LOCAL
                push(vm, vm->frames[vm->fp - 1].locals.data[instr.arg.value]);
                break;
            
            case 0x1A: // RETURN
                free(vm->frames[vm->fp - 1].locals.data);
                vm->pc = vm->frames[--vm->fp].return_address;
                vm->fp--;
                break;

            case 0x1B: // BUILD_LIST
                result.type = ARRAY_TYPE;
                result.value = vm->asp++;

                aux = result.value;
                length = (instr.arg.value < 4) ? 4 : (instr.arg.value + 3) & ~3u;
                create_array(&vm->array_storage[aux], length);
                
                for (int i = 0; i < instr.arg.value; i++) {
                    left = pop(vm);
                    if (i == 0) vm->array_storage[aux].type = left.type;
                    append_array(&vm->array_storage[aux], left.value);
                }

                push(vm, result);
                aux = vm->memory[vm->pc].opcode;
                break;
            
            case 0x1C: // LIST_ACCESS
                index = (instr.arg.value == -1) ? pop(vm).value : instr.arg.value;
                array_access = pop(vm).value;
                
                result.type = vm->array_storage[array_access].type;
                result.value = vm->array_storage[array_access].items[index];

                push(vm, result);
                break;
            
            case 0x1D: // LIST_SET
                index = (instr.arg.value == -1) ? pop(vm).value : instr.arg.value;
                array_access = pop(vm).value;
                vm->array_storage[array_access].items[index] = pop(vm).value;
                break;

            case 0x1E: // BUILD_STR
                result.type = ARRAY_TYPE;
                result.value = vm->asp++;

                aux = result.value;
                length = (instr.arg.value < 4) ? 4 : (instr.arg.value + 3) & ~3u;
                create_array(&vm->array_storage[aux], length);
                
                vm->array_storage[aux].type = CHAR_TYPE;
                for (int i = 0; i < instr.arg.value; i++) {
                    left = pop(vm);
                    append_array(&vm->array_storage[aux], left.value);
                }

                push(vm, result);
                aux = vm->memory[vm->pc].opcode;
                break;

            case 0xFF: // SYSCALL
                syscall(vm, instr.arg.value);
                break;
        }
    } while (vm->pc < size);
}

int main(int argc, char* argv[]) {
    const char* filename = (argc < 2) ? "output.bin" : argv[1];

    VM virtual_machine;
    int size = load_program(&virtual_machine, filename);
    run(&virtual_machine, size);

    return 0;
}
