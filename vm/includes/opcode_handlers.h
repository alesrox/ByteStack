#pragma once
#include "../virtual_machine.h"
#include "strucs-type.h"
#include "syscall.h"

typedef void (*OpcodeHandler)(VM *vm, Instruction instr);
void run_function(VM* vm, uint32_t func_id);

void handle_store(VM *vm, Instruction instr);
void handle_store_byte(VM *vm, Instruction instr);
void handle_store_float(VM *vm, Instruction instr);
void handle_store_mem(VM *vm, Instruction instr);
void handle_load(VM *vm, Instruction instr);
void handle_jump(VM *vm, Instruction instr);
void handle_jump_if(VM *vm, Instruction instr);
void handle_call(VM *vm, Instruction instr);
void handle_return(VM *vm, Instruction instr);
void handle_build_list(VM *vm, Instruction instr);
void handle_list_access(VM *vm, Instruction instr);
void handle_list_set(VM *vm, Instruction instr);
void handle_build_str(VM *vm, Instruction instr);
void handle_store_char(VM *vm, Instruction instr);
void handle_define_type(VM *vm, Instruction instr);
void handle_new(VM *vm, Instruction instr);
void handle_store_heap(VM *vm, Instruction instr);
void handle_load_heap(VM *vm, Instruction instr);
void handle_cast(VM *vm, Instruction instr);
void handle_objcall(VM *vm, Instruction instr);
void handle_syscall(VM *vm, Instruction instr);
