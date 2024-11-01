#include <math.h>
#include "virtual_machine.h"

float extract_float(DataItem item) {
    if (item.type == FLOAT_TYPE)
        return *((float*)&item.value);

    return (float)item.value;
}

float float_mod(float a, float b) {
    return a - b * floorf(a / b);
}