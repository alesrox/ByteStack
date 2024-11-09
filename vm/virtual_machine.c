#include "virtual_machine.h"

char* error_messages[ERR_COUNT] = {
    "Error: Binary file not found",
    "Error: Maximum recursion depth exceeded",
    "Error: Memory access out of bounds",
    "Error: Attempted to access an empty stack",
    "Error: Tried to store incorrect type on a array"
};

void throw_error(char* msg) {
    printf("\n");
    perror(msg);
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
        vm->memory[i].arg.type = (vm->memory[i].opcode == 0x1F) ? FLOAT_TYPE : INT_TYPE; 
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
        DataItem n1, n2, result;
        int address, index, array_access, aux, length;

        // printf("0x%02X - %d\n", instr.opcode, instr.arg.value);
        switch (instr.opcode) {
            case 0x01: // ADD
                n1 = pop(vm);
                n2 = pop(vm);

                if (n1.type == FLOAT_TYPE || n2.type == FLOAT_TYPE) {
                    result.type = FLOAT_TYPE;
                    result.value = extract_float(n1) + extract_float(n2);
                } else {
                    result.type = INT_TYPE;
                    result.value = n1.value + n2.value;
                }

                push(vm, result);
                break;

            case 0x02: // SUB
                n1 = pop(vm);
                n2 = pop(vm);

                if (n1.type == FLOAT_TYPE || n2.type == FLOAT_TYPE) {
                    result.type = FLOAT_TYPE;
                    result.value = extract_float(n1) - extract_float(n2);
                } else {
                    result.type = INT_TYPE;
                    result.value = n1.value - n2.value;
                }

                push(vm, result);
                break;

            case 0x03: // MUL
                n1 = pop(vm);
                n2 = pop(vm);

                if (n1.type == FLOAT_TYPE || n2.type == FLOAT_TYPE) {
                    result.type = FLOAT_TYPE;
                    result.value = extract_float(n1) * extract_float(n2);
                } else {
                    result.type = INT_TYPE;
                    result.value = n1.value * n2.value;
                }

                push(vm, result);
                break;

            case 0x04: // DIV
                n1 = pop(vm);
                n2 = pop(vm);

                result.type = FLOAT_TYPE;
                result.value = extract_float(n1) / extract_float(n2);

                push(vm, result);
                break;

            case 0x05: // MOD
                n1 = pop(vm);
                n2 = pop(vm);

                if (n1.type == FLOAT_TYPE || n2.type == FLOAT_TYPE) {
                    result.type = FLOAT_TYPE;
                    result.value = float_mod(extract_float(n1), extract_float(n2));
                } else {
                    result.type = INT_TYPE;
                    result.value = n1.value % n2.value;
                }

                push(vm, result);
                break;

            case 0x06: // AND
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (n1.value && n2.value);

                push(vm, result);
                break;

            case 0x07: // OR
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (n1.value || n2.value);

                push(vm, result);
                break;

            case 0x08: // NOT
                n1 = pop(vm);
                result.type = INT_TYPE;
                result.value = !n1.value;

                push(vm, result);
                break;

            case 0x09: // EQ
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (
                    ((n1.type == FLOAT_TYPE) ? extract_float(n1) : (int) n1.value)
                    ==
                    ((n2.type == FLOAT_TYPE) ? extract_float(n2) : (int) n2.value)
                );

                push(vm, result);
                break;

            case 0x0A: // NEQ
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (
                    ((n1.type == FLOAT_TYPE) ? extract_float(n1) : (int) n1.value)
                    !=
                    ((n2.type == FLOAT_TYPE) ? extract_float(n2) : (int) n2.value)
                );

                push(vm, result);
                break;

            case 0x0B: // LT
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;

                result.value = (
                    ((n2.type == FLOAT_TYPE) ? extract_float(n2) : (int) n2.value)
                    <
                    ((n1.type == FLOAT_TYPE) ? extract_float(n1) : (int) n1.value)
                );

                push(vm, result);
                break;

            case 0x0C: // GT
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (
                    ((n2.type == FLOAT_TYPE) ? extract_float(n2) : (int) n2.value)
                    >
                    ((n1.type == FLOAT_TYPE) ? extract_float(n1) : (int) n1.value)
                );

                push(vm, result);
                break;

            case 0x0D: // LE
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (
                    ((n2.type == FLOAT_TYPE) ? extract_float(n2) : (int) n2.value)
                    <=
                    ((n1.type == FLOAT_TYPE) ? extract_float(n1) : (int) n1.value)
                );

                push(vm, result);
                break;

            case 0x0E: // GE
                n1 = pop(vm);
                n2 = pop(vm);
                result.type = INT_TYPE;
                result.value = (
                    ((n2.type == FLOAT_TYPE) ? extract_float(n2) : (int) n2.value)
                    >=
                    ((n1.type == FLOAT_TYPE) ? extract_float(n1) : (int) n1.value)
                );

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
                n1 = pop(vm);
                store_data(&vm->frames[vm->fp - 1].locals, instr.arg.value, n1);
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
                    n1 = pop(vm);
                    if (i == 0) vm->array_storage[aux].type = n1.type;
                    append_array(&vm->array_storage[aux], n1.value);
                }

                push(vm, result);
                aux = vm->memory[vm->pc].opcode;
                if (aux == 255) vm->asp--;
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
                    n1 = pop(vm);
                    append_array(&vm->array_storage[aux], n1.value);
                }

                push(vm, result);
                aux = vm->memory[vm->pc].opcode;
                if (aux != 17 && aux != 24) vm->asp--;
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
