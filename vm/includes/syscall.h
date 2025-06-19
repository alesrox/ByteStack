#include "../virtual_machine.h"

#include "alu.h"
#include "errors.h"
#include "stack.h"
#include "structs-type.h"

#include <stdlib.h>
#include <stdio.h>
#include <math.h>

void syscall(VM *vm, int arg);
void built_in_subprint(Item item, FILE *out);

// System Functions
void built_in_exit(VM*);
void built_in_print(VM*);
void built_in_input(VM*);
void built_in_getf(VM*);
void built_in_scan(VM*);
void built_in_type(VM*);
void built_in_read(VM*);
void built_in_write(VM*);

// List Functions
void built_in_size(VM*);
void built_in_size(VM*);
void built_in_append(VM*);
void built_in_remove_at(VM*);
void built_in_is_empty(VM*);
void built_in_map(VM*);
void built_in_slice(VM*);
void built_in_filter(VM*);
void built_in_min(VM*);
void built_in_max(VM*);
void built_in_lower(VM*);
void built_in_upper(VM*);
void built_in_toString(VM*);