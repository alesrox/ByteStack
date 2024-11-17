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

void remove_at(DynamicArray* array, int index) {
    if (index < 0 || index >= array->size) {
        throw_error(error_messages[ERR_OUT_OF_BOUNDS]);
    }

    for (int i = index; i < array->size - 1; i++) {
        array->items[i] = array->items[i + 1];
    }

    array->size--;

    if (array->size > 0 && array->size < array->capacity / 4) {
        resize_array(array, array->capacity / 2);
    }
}

void remove_last(DynamicArray *array) {
    if (array->size > 0) {
        array->size--;
        if (array->size > 0 && array->size < array->capacity / 4)
            resize_array(array, array->capacity / 2);  // Reducir capacidad
    }
}

// String utils 
void convert_int_to_str(DynamicArray *arr, uint32_t integer) {
    int value = integer;
    int digits[10], digit_count = 0;

    if (value < 0) {
        append_array(arr, 45); // -
        value = -value;
    }

    do {
        digits[digit_count++] = value % 10;
        value /= 10;
    } while (value > 0);


    for (int i = digit_count - 1; i >= 0; i--)
        append_array(arr, 48 + digits[i]);
}

void convert_float_to_str(DynamicArray *arr, uint32_t float_num) {
    DataItem aux = {FLOAT_TYPE, float_num};
    float value = extract_float(aux);

    if (value < 0) {
        append_array(arr, 45); // -
        value = -value;
    }

    int integer_part = (int) value;
    float fractional_part = value - integer_part;

    convert_int_to_str(arr, integer_part);

    if (fractional_part > 0) {
        append_array(arr, 46); // .
        // Limit to 6 decimals
        for (int i = 0; i < 8 && fractional_part > 0.0001; i++) { 
            fractional_part *= 10;
            int digit = (int) fractional_part;
            append_array(arr, 48 + digit);
            fractional_part -= digit;
        }
    }
}

void convert_list_to_str(VM* vm, DynamicArray* arr, DynamicArray list) {
    append_array(arr, (uint32_t) '[');

    void (*convert_func)(DynamicArray*, uint32_t);
    convert_func = (list.type == INT_TYPE) ? convert_int_to_str : convert_float_to_str;

    for (int i = 0; i < list.size; i++) {
        (list.type == ARRAY_TYPE) ? convert_list_to_str(vm, arr, vm->array_storage[list.items[i]]) : convert_func(arr, list.items[i]);
        if (i != list.size - 1) append_array(arr, (uint32_t) ',');
    }

    append_array(arr, (uint32_t) ']');
}
