#include "virtual_machine.h"

char* get_type[ARRAY_TYPE + 1] = {
    "UNASSIGNED", "INT", "FLOAT",
    "CHAR", "ARRAY"
};

void show_vm_state(VM vm) {
    Instruction instr = vm.memory[vm.pc - 1];
    printf("\n-----------------\n");
    printf("PC: %d -> 0x%02X %g\n", vm.pc - 1, instr.opcode, extract_float(instr.arg));
    
    printf("Stack: [");
    for (int i = 0; i < vm.sp; i++) {
        DataItem item = vm.stack[i];
        printf("{%s, %d}", get_type[item.type], item.value);
        if (i != vm.sp - 1) printf(", ");
    }
    printf("]\nFrame: %d", vm.fp);
    if (instr.opcode == 0xFF && instr.arg.value == 1) printf("\nOutput: ");
    if (instr.opcode == 0xFF && instr.arg.value == 2) printf("\nInput: ");
}