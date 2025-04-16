#pragma once
#include "strucs-type.h"
#include "errors.h"
#include <stdlib.h>
#include <string.h>

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

void memory_init(Memory *mem);
void memory_destroy(Memory *mem);

int memory_write(Memory *mem, uint32_t address, uint32_t value, size_t size);
int memory_read(Memory *mem, uint32_t address, uint32_t *value, size_t size);
int memory_expand(Memory *mem, size_t new_size);

void heap_init(Heap *heap);
void heap_destroy(Heap *heap);

size_t heap_add_block(Heap *heap, DataType type);
int heap_write(Heap *heap, size_t index, uint32_t value, size_t offset, size_t size);
int heap_read(Heap *heap, size_t index, uint32_t *value, size_t offset, size_t size);