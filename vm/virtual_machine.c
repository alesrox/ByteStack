#include "virtual_machine.h"

int debuging = 0;
char* error_messages[ERR_COUNT] = {
    "File not found",
    "Maximum recursion depth exceeded",
    "Memory access out of bounds",
    "Attempted to access an empty stack",
    "Tried to store incorrect type, casting not possible",
    "Index out of bounds",
    "Failed to open file, please check permissions",
    "Attempted to write a complex structure in an unsupported format",
    "Attempted to write a complex structure to a binary file, which is not allowed",
};

void throw_error(char* msg) {
    printf("\nExecution error: %s", msg);
    exit(EXIT_FAILURE);
}

void init_vm(VM *vm) {
    vm->memory.pointer = 0;
    vm->memory.capacity = MEMORY_SIZE;
    vm->memory.data = malloc(sizeof(DataItem) * vm->memory.capacity);

    vm->heap.pointer = 0;
    vm->heap.capacity = STACK_SIZE;
    vm->heap.data = malloc(sizeof(DataItem) * vm->heap.capacity);

    vm->array_storage = malloc(sizeof(DynamicArray) * 4);
    vm->num_instr = 0;

    vm->pc = 0;
    vm->asp = 0;
    vm->stack_pointer = 0;
    vm->frame_pointer = -1;
}

void load_program(VM *vm, const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (!file) throw_error(error_messages[ERR_FILE_NOT_FOUND]);
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    int num_instructions = size/5;
    vm->num_instr = num_instructions;
    vm->instruction_memory = malloc(sizeof(Instruction) * (num_instructions + 1));

    for (int i = 0; i < num_instructions; i++) {
        fread(&vm->instruction_memory[i].opcode, sizeof(uint8_t), 1, file);
        vm->instruction_memory[i].arg.type = UNASSIGNED_TYPE; 
        fread(&vm->instruction_memory[i].arg.value, sizeof(uint32_t), 1, file);
    }

    fclose(file);
}

void run(VM *vm) {
    do {
        Instruction instr = vm->instruction_memory[vm->pc++];
        DataItem left, right, result;
        int address, index, array_access, aux, length;

        if (debuging) show_vm_state(*vm);
        if (vm->asp % 4 == 0)
            vm->array_storage = realloc(vm->array_storage, (vm->asp + 4) * sizeof(DynamicArray));

        if (instr.opcode < 0x0F) {
            right = (instr.opcode != 0x08) ? pop(vm) : (DataItem){0, 0};
            left = pop(vm);

            if (right.type <= 3 && left.type <= 3) { // Only ints or floats
                result = alu(vm, left, right, instr.opcode);
                push(vm, result);
            } else if (right.type == ARRAY_TYPE ^ left.type == ARRAY_TYPE) {
                DynamicArray* arr = &vm->array_storage[(right.type == ARRAY_TYPE) ? right.value : left.value];
                DataItem item = (right.type != ARRAY_TYPE) ? right : left;

                if (arr->type == CHAR_TYPE) {
                    void (*convert_func)(DynamicArray*, uint32_t);
                    convert_func = (item.type == INT_TYPE) ? convert_int_to_str : convert_float_to_str;
                    convert_func(arr, item.value);
                } else append_array(arr, item.value);

                push(vm, (right.type == ARRAY_TYPE) ? right : left);
            } else /* if (right.type == ARRAY_TYPE && left.type == ARRAY_TYPE) */ {
                DynamicArray* left_arr = &vm->array_storage[left.value];
                DynamicArray* right_arr = &vm->array_storage[right.value];

                for (int i = 0; i < right_arr->size; i++)
                    append_array(left_arr, right_arr->items[i]);
                    
                push(vm, left);
            }
            continue;
        }

        switch (instr.opcode) {
            case 0x0F: // STORE
                instr.arg.type = INT_TYPE;
                push(vm, instr.arg);
                break;

            case 0x10: // STORE_FLOAT
                instr.arg.type = FLOAT_TYPE;
                push(vm, instr.arg);
                break;

            case 0x11: // STORE_MEM
                result = pop(vm);
                store_data(vm, &vm->memory, instr.arg.value, result);
                break;

            case 0x12: // LOAD
                push(vm, vm->memory.data[instr.arg.value]);
                break;

            case 0x13: // JUMP
                vm->pc = instr.arg.value;
                break;

            case 0x14: // JUMP_IF
                if (pop(vm).value) 
                    vm->pc = instr.arg.value;
                break;

            case 0x15: // CALL
                run_function(vm, (instr.arg.value == -1) ? pop(vm).value : vm->memory.data[instr.arg.value].value);
                break;
            
            case 0x16: // RETURN
                vm->pc = vm->return_address[vm->frame_pointer--];
                return;

            case 0x17: // BUILD_LIST
                result.type = ARRAY_TYPE;
                result.value = vm->asp++;

                aux = result.value;
                length = (instr.arg.value < 4) ? 4 : (instr.arg.value + 3) & ~3u;
                init_array(&vm->array_storage[aux], length);
                
                for (int i = 0; i < instr.arg.value; i++) {
                    left = pop(vm);
                    if (i == 0) vm->array_storage[aux].type = left.type;
                    append_array(&vm->array_storage[aux], left.value);
                }

                push(vm, result);
                break;
            
            case 0x18: // LIST_ACCESS
                index = (instr.arg.value == -1) ? pop(vm).value : instr.arg.value;
                array_access = pop(vm).value;
                
                result.type = vm->array_storage[array_access].type;
                result.value = vm->array_storage[array_access].items[index];

                push(vm, result);
                break;
            
            case 0x19: // LIST_SET
                index = (instr.arg.value == -1) ? pop(vm).value : instr.arg.value;
                array_access = pop(vm).value;
                vm->array_storage[array_access].items[index] = pop(vm).value;
                break;

            case 0x1A: // BUILD_STR
                result.type = ARRAY_TYPE;
                result.value = vm->asp++;

                aux = result.value;
                length = (instr.arg.value < 4) ? 4 : (instr.arg.value + 3) & ~3u;
                init_array(&vm->array_storage[aux], length);
                
                vm->array_storage[aux].type = CHAR_TYPE;
                for (int i = 0; i < instr.arg.value; i++) {
                    left = pop(vm);
                    append_array(&vm->array_storage[aux], left.value);
                }

                push(vm, result);
                break;
            
            case 0x1B: // STORE_CHAR
                instr.arg.type = CHAR_TYPE;
                push(vm, instr.arg);
                break;
            
            case 0x1C: // DEFINE_TYPE
                store_data(vm, &vm->heap, -1, instr.arg);

                for (int i = 0; i < (int) instr.arg.value; i++) {
                    store_data(vm, &vm->heap, -1, pop(vm));
                }

                break;
            
            case 0x1D: // NEW
                address = vm->heap.pointer;
                store_data(vm, &vm->heap, -1, (DataItem){OBJ_TYPE, instr.arg.value});
                for (int i = 0; i < vm->heap.data[instr.arg.value].value; i++) {
                    store_data(vm, &vm->heap, -1, pop(vm));
                }

                push(vm, (DataItem){OBJ_TYPE, address});
                break;

            case 0x1E: // STORE_HEAP
                store_data(vm, &vm->heap, pop(vm).value + instr.arg.value, pop(vm));
                break;

            case 0x1F: // LOAD_HEAP
                push(vm, vm->heap.data[pop(vm).value + instr.arg.value]);
                break;
            
            case 0x20: // CAST
                right = pop(vm);
                if (instr.arg.value <= 1 && right.type == 2) {
                    right.type = 1;
                    right.value = (uint32_t)(int) extract_float(right);
                } else if (instr.arg.value == 2 && right.type == 1) {
                    right.type = 2;
                    float temp = extract_float(right);
                    right.value = *(uint32_t*)&temp;
                }
                push(vm, right);
                break;

            case 0xFE: // OBJCALL # TODO: REPLACE
                objcall(vm, instr.arg.value);
                break;

            case 0xFF: // SYSCALL
                syscall(vm, instr.arg.value);
                break;
        }
    } while (vm->pc < vm->num_instr);
}

int main(int argc, char* argv[]) {
    const char* filename = (argc < 2) ? "output.o" : argv[1];
    if (argc > 2 && argv[2][0] == '-' && argv[2][1] == 'd' && argv[2][2] == '\0') debuging = 1;
    if (debuging) printf("Debug mode is ON.");

    VM virtual_machine;
    init_vm(&virtual_machine);
    load_program(&virtual_machine, filename);
    run(&virtual_machine);
    if (debuging) { virtual_machine.pc++; show_vm_state(virtual_machine); }

    return 0;
}
