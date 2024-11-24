#include "virtual_machine.h"

char* get_type[ARRAY_TYPE + 1] = {
    "UNASSIGNED", "INT", "FLOAT",
    "CHAR", "ARRAY"
};

void show_vm_state(VM vm) {
    Instruction instr = vm.memory[vm.pc - 1];
    printf("\n-----------------\n");
    if (instr.arg.type == FLOAT_TYPE)
        printf("PC: %d -> 0x%02X %g\n", vm.pc - 1, instr.opcode, extract_float(instr.arg));
    else
        printf("PC: %d -> 0x%02X %d\n", vm.pc - 1, instr.opcode, instr.arg.value);
    
    printf("Stack: [");
    for (int i = 0; i < vm.sp; i++) {
        DataItem item = vm.stack[i];
        printf("{%s, %d}", get_type[item.type], item.value);
        if (i != vm.sp - 1) printf(", ");
    }

    printf("]\nMemory: [");
    for (int i = 0; i < vm.data_segment.pointer; i++) {
        DataItem item = vm.data_segment.data[i];
        printf("{%s, %d}", get_type[item.type], item.value);
        if (item.type == ARRAY_TYPE) {
            DynamicArray arr = vm.array_storage[item.value];
            if (arr.type == CHAR_TYPE) printf(" -> \"");
            else printf(" -> %s:[", get_type[arr.type]);
            for (int i = 0; i < arr.size; i++) {
                built_in_subprint((DataItem){arr.type, arr.items[i]}, stdout);
                if (arr.type != CHAR_TYPE && i < arr.size - 1) printf(", ");
            }
            
            printf((arr.type == CHAR_TYPE) ? "\"" : "]");
        }
        if (i != vm.data_segment.pointer - 1) printf(", ");
    }
    
    if (vm.fp != 0) {
        printf("]\nLocals: [");
        for (int i = 0; i < vm.frames[vm.fp - 1].locals.pointer; i++) {
            DataItem item = vm.frames[vm.fp - 1].locals.data[i];
            printf("{%s, %d}", get_type[item.type], item.value);
            if (item.type == ARRAY_TYPE) {
                DynamicArray arr = vm.array_storage[item.value];
                if (arr.type == CHAR_TYPE) printf(" -> \"");
                else printf(" -> %s:[", get_type[arr.type]);
                for (int i = 0; i < arr.size; i++) {
                    built_in_subprint((DataItem){arr.type, arr.items[i]}, stdout);
                    if (arr.type != CHAR_TYPE && i < arr.size - 1) printf(", ");
                }
                
                printf((arr.type == CHAR_TYPE) ? "\"" : "]");
            }
            if (i != vm.frames[vm.fp - 1].locals.pointer - 1) printf(", ");
        }
    }

    printf("]\nFrame: %d", vm.fp);
    if (instr.opcode == 0xFF && instr.arg.value == 1) printf("\nOutput: ");
    if (instr.opcode == 0xFF && instr.arg.value == 2) printf("\nInput: ");
}