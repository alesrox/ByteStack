#pragma once
#include "structs-type.h"
#include "errors.h"
#include <stdlib.h>
#include <string.h>

extern size_t sizes[POINTER_TYPE + 1];

typedef struct {
    uint8_t *data;
    DataType *table_type;
    size_t size;
} Memory;

typedef struct {
    Memory *blocks;
    DataType *table_type;
    size_t size;
} Heap;

void memory_init(Memory*);
void memory_destroy(Memory*);

int memory_write(Memory*, uint32_t, uint32_t, size_t);
int memory_read(Memory*, uint32_t, uint32_t*, size_t);
int memory_expand(Memory*, size_t);

void heap_init(Heap*);
void heap_destroy(Heap*);

size_t heap_add_block(Heap*, DataType);
size_t duplicate_heap_block(Heap*, size_t, DataType, int);
int heap_write(Heap*, size_t, uint32_t, size_t, size_t);
int heap_read(Heap*, size_t, uint32_t*, size_t, size_t);
int heap_remove_element(Heap*, size_t, size_t, size_t);