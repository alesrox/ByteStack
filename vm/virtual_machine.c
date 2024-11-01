#include "virtual_machine.h"

char* error_messages[ERR_COUNT] = {
    "Error: Binary file not found",
    "Error: Maximum recursion depth exceeded",
    "Error: Memory access out of bounds",
    "Error: Attempted to access an empty stack",
    "Error: Tried to store incorrect type on a array"
};

void throw_error(char* msg) {
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

    vm->memory = malloc(sizeof(Instruction) * num_instructions);
    for (int i = 0; i < num_instructions; i++) {
        fread(&vm->memory[i].opcode, sizeof(uint8_t), 1, file);
        vm->memory[i].arg.type = (vm->memory[i].opcode == 0x1F) ? FLOAT_TYPE : INT_TYPE; 
        fread(&vm->memory[i].arg.value, sizeof(uint32_t), 1, file);
        //printf("opcode: %02X\n", vm->memory[i].opcode);
    }

    fclose(file);

    vm->pc = 0;
    vm->mp = 0;
    vm->sp = 0;
    vm->fp = 0;
    vm->asp = 0;

    return num_instructions;
}

void run(VM *vm, int size) {
    do {
        Instruction instr = vm->memory[vm->pc++];
        DataItem n1, n2, result;
        int index, array_access;

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
                if (instr.arg.value == -1) {
                    vm->data_memory[vm->mp++] = pop(vm);
                } else {
                    vm->data_memory[instr.arg.value] = pop(vm);
                }
                break;

            case 0x12: // LOAD
                push(vm, vm->data_memory[instr.arg.value]);
                break;

            case 0x13: // JUMP
                vm->pc = instr.arg.value;
                break;

            case 0x14: // JUMP_IF
                if (pop(vm).value) 
                    vm->pc = instr.arg.value;
                break;
            
            case 0x15: // CREATE_SCOPE
                if (vm->fp == IN_SIZE) throw_error(error_messages[ERR_RECURSION_LIMIT]);
                vm->frames[vm->fp++].lp = 0;
                break;
            
            case 0x16: // DEL_SCOPE
                vm->fp--;
                break;

            case 0x17: // CALL
                if (vm->fp == IN_SIZE) throw_error(error_messages[ERR_RECURSION_LIMIT]);
                vm->frames[vm->fp++].return_address = vm->pc;
                vm->frames[vm->fp].lp = 0;
                vm->pc = instr.arg.value;
                break;

            case 0x18: // STORE_LOCAL
                if (instr.arg.value == -1) {
                    vm->frames[vm->fp].locals[vm->frames[vm->fp].lp++] = pop(vm);
                } else {
                    vm->frames[vm->fp].locals[instr.arg.value] = pop(vm);
                }
                break;
            
            case 0x19: // LOAD_LOCAL
                push(vm, vm->frames[vm->fp].locals[instr.arg.value]);
                break;
            
            case 0x1A: // RETURN
                vm->pc = vm->frames[--vm->fp].return_address;
                break;

            case 0x1B: // BUILD_LIST
                result.type = ARRAY_TYPE;
                result.value = vm->asp++;
                vm->data_memory[vm->mp++] = result;

                int aux = result.value;
                int length = (instr.arg.value < 4) ? 4 : (instr.arg.value + 3) & ~3u;
                create_array(&vm->array_storage[aux], length);
                
                for (int i = 0; i < instr.arg.value; i++) {
                    result = pop(vm);
                    if (i == 0) vm->array_storage[aux].type = result.type;
                    append_array(&vm->array_storage[aux], result.value);
                }
                break;
            
            case 0x1C: // LIST_ACCESS
                index = (instr.arg.value == -1) ? pop(vm).value : instr.arg.value;
                array_access = vm->data_memory[pop(vm).value].value;

                result.type = vm->array_storage[array_access].type;
                result.value = vm->array_storage[array_access].items[index];

                push(vm, result);
                break;
            
            case 0x1D: // LIST_SET
                index = (instr.arg.value == -1) ? pop(vm).value : instr.arg.value;
                array_access = vm->data_memory[pop(vm).value].value;
                result = pop(vm);

                if (result.type != vm->array_storage[array_access].type)
                    throw_error(error_messages[ERR_BAD_TYPE_ARR]);

                vm->array_storage[array_access].items[index] = result.value;
                break;

            case 0xFF: // SYSCALL
                syscall(vm, instr.arg.value);
                break;
        }

        if (vm->mp == MEMORY_SIZE) throw_error(error_messages[ERR_MEMORY_OUT_OF_BOUNDS]);
    } while (vm->pc < size);
}

int main(int argc, char* argv[]) {
    const char* filename = (argc < 2) ? "output.bin" : argv[1];

    VM virtual_machine;
    int size = load_program(&virtual_machine, filename);
    run(&virtual_machine, size);

    return 0;
}
