#include "../includes/stack.h"

void print_stack(const Stack stack) {
    printf("Stack: ");
    for (int i = stack.top; i >= 0; i--) {
        printf("[%d|%d], ", stack.data[i].type, stack.data[i].value);
    }
    printf("\n");
}

void stack_init(Stack *stack) {
    stack->top = -1;
}

void push(Stack *stack, Item item) {
    if (stack->top >= STACK_SIZE)
        handle_error(STACK_OVERFLOW);

    stack->data[++stack->top] = item;
}

Item pop(Stack *stack) {
    if (stack->top < 0)
        handle_error(STACK_UNDERFLOW);

    return stack->data[stack->top--];
}
