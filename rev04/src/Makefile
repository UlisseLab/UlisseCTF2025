CC = gcc
CFLAGS = -s
TARGET = delirivm
BYTECODE = delirivm_bytecode
BYTECODE_ASM = $(BYTECODE).asm
PY_SCRIPT = bytecode_generator.py


all: $(TARGET) $(BYTECODE)

$(TARGET): vm.c
	$(CC) $(CFLAGS) -o $(TARGET) vm.c

$(BYTECODE): $(PY_SCRIPT)
	python3 $(PY_SCRIPT)

clean:
	rm -f $(TARGET) $(BYTECODE) $(BYTECODE_ASM)

deploy: all
	cp $(TARGET) ../attachments/
	cp $(BYTECODE) ../attachments/
	make clean
