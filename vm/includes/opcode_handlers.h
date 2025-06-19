#pragma once
#include "../virtual_machine.h"
#include "structs-type.h"
#include "syscall.h"

typedef void (*OpcodeHandler)(VM*, Instruction);
void run_function(VM*, uint32_t);

void handle_store(VM*, Instruction);
void handle_store_byte(VM*, Instruction);
void handle_store_float(VM*, Instruction);
void handle_store_mem(VM*, Instruction);
void handle_load(VM*, Instruction);
void handle_jump(VM*, Instruction);
void handle_jump_if(VM*, Instruction);
void handle_call(VM*, Instruction);
void handle_return(VM*, Instruction);
void handle_build_list(VM*, Instruction);
void handle_list_access(VM*, Instruction);
void handle_list_set(VM*, Instruction);
void handle_store_char(VM*, Instruction);
void handle_define_type(VM*, Instruction);
void handle_new(VM*, Instruction);
void handle_cast(VM*, Instruction);
void handle_objcall(VM*, Instruction);
void handle_syscall(VM*, Instruction);
