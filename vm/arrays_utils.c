#include "virtual_machine.h"

void create_array(DynamicArray *array, int initial_capacity) {
    array->items = malloc(initial_capacity * sizeof(uint32_t));
    array->size = 0;
    array->capacity = initial_capacity;
}

void resize_array(DynamicArray *array, int new_capacity) {
    array->items = realloc(array->items, new_capacity * sizeof(int));
    array->capacity = new_capacity;
}

void append_array(DynamicArray *array, uint32_t value) {
    if (array->size == array->capacity)
        resize_array(array, array->capacity * 2);
    array->items[array->size++] = value;
}

void remove_last(DynamicArray *array) {
    if (array->size > 0) {
        array->size--;
        if (array->size > 0 && array->size < array->capacity / 4)
            resize_array(array, array->capacity / 2);  // Reducir capacidad
    }
}
