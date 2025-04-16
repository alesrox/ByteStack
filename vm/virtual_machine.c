#include "virtual_machine.h"
#include "includes/opcode_handlers.h"

void vm_init(VM *vm, const char *filename) {
    stack_init(&vm->stack);
    memory_init(&vm->memory);
    heap_init(&vm->heap);
    
    FILE *file = fopen(filename, "rb");
    if (!file) handle_error(FILE_NOT_FOUND);
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    vm->frame_pointer = 0;
    vm->program_size = size/5;
    vm->bytecode = malloc(sizeof(Instruction) * (vm->program_size + 1));
    vm->pc = vm->bytecode;

    for (int i = 0; i < vm->program_size; i++) {
        fread(&vm->bytecode[i].opcode, sizeof(uint8_t), 1, file);
        fread(&vm->bytecode[i].arg, sizeof(uint32_t), 1, file);
    }

    fclose(file);
}

void vm_destroy(VM *vm) {
    if (!vm) return;

    if (vm->bytecode) {
        free(vm->bytecode);
        vm->bytecode = NULL;
    }

    memory_destroy(&vm->memory);
    heap_destroy(&vm->heap);

    vm->program_size = 0;
    vm->frame_pointer = 0;
    vm->pc = NULL;

    for (int i = 0; i < RECURSION_LIMIT; i++)
        vm->return_address[i] = NULL;
}

OpcodeHandler opcode_handlers[] = {
    [0x0F] = handle_store,
    [0x10] = handle_store_byte,
    [0x11] = handle_store_float,
    [0x12] = handle_store_char,
    [0x13] = handle_store_mem,
    [0x14] = handle_load,
    [0x15] = handle_jump,
    [0x16] = handle_jump_if,
    [0x17] = handle_call,
    [0x18] = handle_return,
    [0x19] = handle_build_list,
    [0x1A] = handle_list_access,
    [0x1B] = handle_list_set,
    [0x1C] = handle_build_str,
    [0x1D] = handle_define_type,
    [0x1E] = handle_new,
    [0x1F] = handle_store_heap,
    [0x20] = handle_load_heap,
    [0x21] = handle_cast,
    [0xFE] = handle_objcall,
    [0xFF] = handle_syscall,
};

void vm_run(VM *vm) {
    while (vm->pc < vm->bytecode + vm->program_size) {
        Instruction instr = *vm->pc++;
        instr_pc_log = instr.opcode;

        if (instr.opcode < 0x0F) {
            alu(&vm->stack, instr.opcode);
            continue;
        }

        OpcodeHandler handler = opcode_handlers[instr.opcode];
        if (!handler) handle_error(UNDEFINED_ERROR);
        handler(vm, instr);
    }
}

int main(int argc, char* argv[]) {
    const char* filename = (argc < 2) ? "output.o" : argv[1];

    VM virtual_machine;
    vm_init(&virtual_machine, filename);
    vm_run(&virtual_machine);
    vm_destroy(&virtual_machine);

    return 0;
}