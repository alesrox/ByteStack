#include "../includes/memory.h"

size_t sizes[POINTER_TYPE + 1] = {
    [UNASSIGNED_TYPE] = 4,
    [BOOL_TYPE]  = 1,
    [INT_TYPE]   = 4,
    [FLOAT_TYPE] = 4,
    [CHAR_TYPE]  = 1,
    [POINTER_TYPE] = 4
};

void memory_init(Memory *mem) {
    mem->data = malloc(sizeof(uint8_t));
    mem->table_type = malloc(sizeof(DataType));
    mem->size = 0;
}

void memory_destroy(Memory *mem) {
    if (mem->data) {
        free(mem->data);
        mem->data = NULL;
    }

    if (mem->table_type) {
        free(mem->table_type);
        mem->table_type = NULL;
    }

    mem->size = 0;
}

int memory_expand(Memory *mem, size_t new_size) {
    if (new_size <= mem->size) return 0;

    uint8_t *new_data = realloc(mem->data, new_size);
    DataType *new_table_type = realloc(mem->table_type, new_size);
    if (!new_data) return -1;

    mem->data = new_data;
    mem->table_type = new_table_type;
    mem->size = new_size;

    return 0;
}

int memory_write(Memory *mem, uint32_t address, uint32_t value, size_t size) {
    if (size == 0 || size > 4) 
        handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);

    if (address == (uint32_t) -1 || mem == NULL) {
        address = mem->size;
        if (memory_expand(mem, address + size) != 0)
            handle_error(UNDEFINED_ERROR);
    }

    if (address + size > mem->size)
        handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);

    for (size_t i = 0; i < size; ++i)
        mem->data[address + i] = (uint8_t)(value >> (8 * i));

    return address;
}

int memory_read(Memory *mem, uint32_t address, uint32_t *value, size_t size) {
    if (size == 0 || size > 4 || address + size > mem->size) {
        printf("%zu %zu %zu\n", size, address + size, mem->size);
        handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);
    }

    *value = 0;
    for (size_t i = 0; i < size; ++i)
        *value |= ((uint32_t)mem->data[address + i]) << (8 * i);

    return 0;
}

void heap_init(Heap *heap) {
    heap->blocks = NULL;
    heap->table_type = NULL;
    heap->size = 0;
}

void heap_destroy(Heap *heap) {
    for (size_t i = 0; i < heap->size; ++i)
        memory_destroy(&heap->blocks[i]);

    free(heap->blocks);
    free(heap->table_type);
    heap->blocks = NULL;
    heap->table_type = NULL;
    heap->size = 0;
}

size_t heap_add_block(Heap *heap, DataType type) {
    Memory *new_blocks = realloc(heap->blocks, sizeof(Memory) * (heap->size + 1));
    DataType *new_types = realloc(heap->table_type, sizeof(DataType) * (heap->size + 1));
    if (new_types == NULL || new_blocks == NULL) return -1;

    heap->blocks = new_blocks;
    heap->table_type = new_types;

    memory_init(&heap->blocks[heap->size]);
    heap->table_type[heap->size] = type;

    heap->size++;
    return heap->size - 1;
}

size_t duplicate_heap_block(Heap *heap, size_t address, DataType to_type, int depth) {
    if (address >= heap->size) handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);
    
    Memory src = heap->blocks[address];
    
    DataType type = (depth == 1) ? to_type : heap->table_type[address];
    size_t new_index = heap_add_block(heap, type);
    if (new_index == -1) return -1;
    
    Memory *dst = &heap->blocks[new_index];
    if (memory_expand(dst, src.size) != 0) return -1;
    
    for (size_t i = 0; i < src.size; i++) {
        if (depth <= 1) {
            uint32_t value;
            heap_read(heap, address, &value, i * sizes[to_type], sizes[to_type]);
            heap_write(heap, new_index, value, i * sizes[to_type], sizes[to_type]);
        } else {
            uint32_t child_address = src.data[i];
            size_t new_child = duplicate_heap_block(heap, child_address, to_type, depth - 1);
            if (new_child == -1) return -1;

            heap_write(heap, new_index, new_child, i, 1);
        }
    }

    return new_index;
}

int heap_write(Heap *heap, size_t index, uint32_t value, size_t offset, size_t size) {
    if (index >= heap->size) handle_error(UNDEFINED_ERROR);

    if (offset == (size_t) -1)
        offset = heap->blocks[index].size;

    if (offset + size > heap->blocks[index].size) 
        memory_expand(&heap->blocks[index], offset + size);
    
    return memory_write(&heap->blocks[index], offset, value, size);
}

int heap_read(Heap *heap, size_t index, uint32_t *value, size_t offset, size_t size) {
    if (index >= heap->size) handle_error(UNDEFINED_ERROR);
    return memory_read(&heap->blocks[index], offset, value, size);
}

int heap_remove_element(Heap *heap, size_t block_index, size_t element_index, size_t element_size) {
    if (block_index >= heap->size) {
        handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);
        return -1;
    }

    Memory *block = &heap->blocks[block_index];
    size_t total_elements = block->size / element_size;

    if (element_index >= total_elements) {
        handle_error(MEMORY_ACCESS_OUT_OF_BOUNDS);
        return -1;
    }

    size_t start = element_index * element_size;
    size_t move_size = (total_elements - element_index - 1) * element_size;

    if (move_size > 0) {
        memmove(block->data + start,
                block->data + start + element_size,
                move_size);
    }

    block->size -= 1;

    return 0;
}