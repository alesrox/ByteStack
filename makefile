PYTHON_VER = 3.10 # Python Version Used: 3.10.6
COMPILER_DIR = compiler

CC = gcc
CFLAGS = -std=c11 -g #-Wall -Wextra
INCLUDES = -Ivm/include -Ivm

SRC_DIR = vm/src
BUILD_DIR = vm/build
MAIN_SRC = vm/virtual_machine.c

MAIN_OBJ = $(BUILD_DIR)/virtual_machine.o
SRC = $(wildcard $(SRC_DIR)/*.c)
OBJ = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SRC))

EXEC = vml

all: $(EXEC)

$(EXEC): $(OBJ) $(MAIN_OBJ)
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $^

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(BUILD_DIR)/virtual_machine.o: vm/virtual_machine.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

test-c: 
	python$(PYTHON_VER) $(COMPILER_DIR)/unit_tests.py

test: vml output.o
	./vml output.o

output.o:
	python$(PYTHON_VER) $(COMPILER_DIR)/main.py examples/example1.lx

clean:
	rm -rf $(BUILD_DIR) $(EXEC) .vscode