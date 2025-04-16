#include "../includes/opcode_handlers.h"

size_t sizes[] = {
    [BOOL_TYPE] = 1,
    [INT_TYPE] = 4,
    [FLOAT_TYPE] = 4,
    [CHAR_TYPE] = 1,
    [ARRAY_TYPE] = 4
};

void run_function(VM* vm, uint32_t func_id) {
    if (vm->frame_pointer > RECURSION_LIMIT) handle_error(MAX_RECURSION_DEPTH_EXCEEDED);
    vm->return_address[vm->frame_pointer++] = vm->pc;
    vm->pc = vm->bytecode + func_id;
    vm_run(vm);
}

void handle_store(VM *vm, Instruction instr) {
    Item data = { INT_TYPE, instr.arg };
    push(&vm->stack, data);
}

void handle_store_byte(VM *vm, Instruction instr) {
    Item arg = { BOOL_TYPE, instr.arg };
    push(&vm->stack, arg);
}

void handle_store_float(VM *vm, Instruction instr) {
    Item arg = { FLOAT_TYPE, instr.arg };
    push(&vm->stack, arg);
}

void handle_store_char(VM *vm, Instruction instr) {
    Item arg = { CHAR_TYPE, instr.arg };
    push(&vm->stack, arg);
}

void handle_store_mem(VM *vm, Instruction instr) {
    Item aux = pop(&vm->stack);
    int address = memory_write(&vm->memory, instr.arg, aux.value, sizes[aux.type]);
    if (address == -1) handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);
    vm->memory.table_type[address] = aux.type;
}

void handle_load(VM *vm, Instruction instr) {
    uint32_t buffer;
    DataType buffer_type = vm->memory.table_type[instr.arg];
    size_t size_buffer = sizes[buffer_type];

    memory_read(&vm->memory, instr.arg, &buffer, size_buffer);
    push(&vm->stack, (Item){ buffer_type, buffer });
}

void handle_jump(VM *vm, Instruction instr) {
    vm->pc = vm->bytecode + instr.arg;
}

void handle_jump_if(VM *vm, Instruction instr) {
    uint32_t aux = pop(&vm->stack).value;
    if (aux == (uint32_t) 1)
        vm->pc = vm->bytecode + instr.arg;
}

void handle_call(VM *vm, Instruction instr) {
    uint32_t dir = (instr.arg == -1) ? pop(&vm->stack).value : vm->memory.data[instr.arg];
    run_function(vm, dir);
}

void handle_return(VM *vm, Instruction instr) {
    vm->pc = vm->return_address[--vm->frame_pointer];
}

void handle_build_list(VM *vm, Instruction instr) {
    Item item = pop(&vm->stack);
    size_t address = heap_add_block(&vm->heap, item.type);
    size_t len = sizes[item.type];
    heap_write(&vm->heap, address, item.value, 0, len);
    
    for (uint32_t i = 1; i < instr.arg; i++) {
        item = pop(&vm->stack);
        heap_write(&vm->heap, address, item.value, i*len, len);
    }

    push(&vm->stack, (Item){ARRAY_TYPE, address});
}

void handle_list_access(VM *vm, Instruction instr) {
    uint32_t value, index; DataType array_type;
    size_t array_location, size_items;

    index = (instr.arg == (uint32_t) -1) ?
        pop(&vm->stack).value : instr.arg;
    
    array_location = pop(&vm->stack).value;
    array_type = vm->heap.table_type[array_location];
    size_items = sizes[array_type];

    heap_read(&vm->heap, array_location, &value, index * size_items, size_items);
    push(&vm->stack, (Item){array_type, value});
}

void handle_list_set(VM *vm, Instruction instr) {
    uint32_t value, index; DataType array_type;
    size_t array_location, size_items;

    index = (instr.arg == (uint32_t) -1) ?
    pop(&vm->stack).value : instr.arg;
    
    array_location = pop(&vm->stack).value;
    value = pop(&vm->stack).value;
    array_type = vm->heap.table_type[array_location];
    size_items = sizes[array_type];
    
    heap_write(&vm->heap, array_location, value, index * size_items, size_items);
}

void handle_build_str(VM *vm, Instruction instr) {
    // TODO: Ya casi jeje
}

// TODO: Replantearse la implementación de structs
void handle_define_type(VM *vm, Instruction instr) {}
void handle_new(VM *vm, Instruction instr) {}

// TODO: ¿Siguen siendo necesarios? Casi seguro que no
void handle_store_heap(VM *vm, Instruction instr) {}
void handle_load_heap(VM *vm, Instruction instr) {}

// TODO: Implementar casting
void handle_cast(VM *vm, Instruction instr) {}

// TODO: ¿Podremos quitarnoslo de encima? Lo dudo, pero se intentará
void handle_objcall(VM *vm, Instruction instr) {}

void handle_syscall(VM *vm, Instruction instr) {
    syscall(vm, instr.arg);
}

