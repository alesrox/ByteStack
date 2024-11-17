#include <math.h>
#include "virtual_machine.h"

uint32_t format_float(float value) {
    return *((uint32_t*) &(value));
}

float extract_float(DataItem item) {
    if (item.type == FLOAT_TYPE){
        return *((float*)&item.value);}

    return (float) ((int) item.value);
}

float float_mod(float a, float b) {
    return a - b * floorf(a / b);
}