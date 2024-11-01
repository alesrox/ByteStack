#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define IN_SIZE 128
#define STACK_SIZE 256
#define MEMORY_SIZE 1024

typedef enum {
    ERR_FILE_NOT_FOUND,
    ERR_RECURSION_LIMIT,
    ERR_MEMORY_OUT_OF_BOUNDS,
    ERR_EMPTY_STACK,
    ERR_BAD_TYPE_ARR,
    ERR_COUNT 
} ErrorCode;

char* error_messages[ERR_COUNT];

typedef enum {
    INT_TYPE,
    FLOAT_TYPE,
    CHAR_TYPE,
    ARRAY_TYPE
} DataType;

typedef struct {
    DataType type;
    uint32_t value;
} DataItem;

typedef struct {
    int size;
    int capacity;
    DataType type;
    uint32_t *items;
} DynamicArray;

typedef struct {
    uint8_t opcode;
    DataItem arg;
} Instruction;

typedef struct {
    int lp; // local pointer
    int return_address;
    DataItem locals[IN_SIZE];
} Frame;

typedef struct {
    int pc; // program count
    int sp; // stack pointer
    int mp; // memory pointer
    int fp; // frame pointer
    int asp; // array storage pointer
    Instruction* memory;
    DataItem stack[STACK_SIZE];
    DataItem data_memory[MEMORY_SIZE];
    Frame frames[IN_SIZE];
    DynamicArray array_storage[1024];
} VM;

// Virtual Machine Control
int load_program(VM *vm, const char *filename);
void run(VM *vm, int size);
void throw_error(char* msg);

// Stack Control
void push(VM *vm, DataItem value);
DataItem pop(VM *vm);
void syscall(VM *vm, int arg);

// Memory Control
void store_data(VM *vm, int address, DataItem item);
DataItem load_data(VM *vm, int address);

// Data Control
float extract_float(DataItem item);
float float_mod(float a, float b);

// Arrays Control
void create_array(DynamicArray *array, int initial_capacity);
void resize_array(DynamicArray *array, int new_capacity);
void append_array(DynamicArray *array, uint32_t value);
void remove_last(DynamicArray *array);

