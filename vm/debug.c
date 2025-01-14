#include "virtual_machine.h"

char* get_type[ARRAY_TYPE + 1] = {
    "UNASSIGNED", "INT", "FLOAT",
    "CHAR", "ARRAY"
};

// Print a DataItem on {type, value} format
void print_data_item(DataItem item, VM* vm) {
    printf("{%s, %d}", get_type[item.type], item.value);

    if (item.type == ARRAY_TYPE) {
        DynamicArray arr = vm->array_storage[item.value];
        if (arr.type == CHAR_TYPE) printf(" -> \"");
        else printf(" -> %s:[", get_type[arr.type]);

        for (int i = 0; i < arr.size; i++) {
            built_in_subprint((DataItem){arr.type, arr.items[i]}, stdout);
            if (arr.type != CHAR_TYPE && i < arr.size - 1) printf(", ");
        }

        printf((arr.type == CHAR_TYPE) ? "\"" : "]");
    }
}

// Print a DataItem list on [item1, item2, ...] format
void print_data_list(DataItem* data, int size, VM* vm) {
    printf("[");
    for (int i = 0; i < size; i++) {
        print_data_item(data[i], vm);
        if (i != size - 1) printf(", ");
    }
    printf("]");
}

void show_vm_state(VM vm) {
    Instruction instr = vm.memory[vm.pc - 1];

    // Print a head
    printf("\n-----------------\n");
    if (instr.arg.type == FLOAT_TYPE)
        printf("PC: %d -> 0x%02X %g\n", vm.pc - 1, instr.opcode, extract_float(instr.arg));
    else
        printf("PC: %d -> 0x%02X %d\n", vm.pc - 1, instr.opcode, instr.arg.value);

    // Print stack state
    printf("Stack: ");
    print_data_list(vm.stack, vm.stack_pointer, &vm);

    // Print data segment
    printf("\nMemory: ");
    print_data_list(vm.data_segment.data, vm.data_segment.pointer, &vm);

    // Print heap
    printf("\nHeap: ");
    print_data_list(vm.heap.data, vm.heap.pointer, &vm);

    // Print locals if exits
    if (vm.frame_pointer != 0) {
        printf("\nLocals: ");
        Frame current_frame = vm.frames[vm.frame_pointer - 1];
        print_data_list(current_frame.locals.data, current_frame.locals.pointer, &vm);
    }

    // Print current frame information
    printf("\nFrame: %d", vm.frame_pointer);

    // Special instructions Input and Output
    if (instr.opcode == 0xFF && instr.arg.value == 1) printf("\nOutput: ");
    if (instr.opcode == 0xFF && instr.arg.value == 2) printf("\nInput: ");
}