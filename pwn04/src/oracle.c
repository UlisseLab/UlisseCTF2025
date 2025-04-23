#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stddef.h>
#include <linux/seccomp.h>  
#include <linux/filter.h>
#include <linux/bpf.h>
#include <sys/prctl.h>
#include <sys/mman.h>
#include <sys/syscall.h>


void readString(char *buffer, int size){
    ssize_t bread = read(0, buffer, size);
    if(buffer[bread-1] == '\n')
        buffer[bread-1] = 0;
    return;
}

int readSize(char *buffer){  
    char *endptr;
    readString(buffer, 17);
    int size = atoi(buffer);
    if (size < 0 || size > 40){
        printf("Invalid size\n");
        exit(0);
    }
    return strtol(buffer, &endptr, 0); // rop
}

const long long MEM_ADDR = 0x13370000;
const long long MEM_SIZE = 0x50;

void setSecurity() {
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD  | BPF_W | BPF_ABS, offsetof(struct seccomp_data, instruction_pointer)),
        BPF_JUMP(BPF_JMP | BPF_JGE, MEM_ADDR, 0, 5),
        BPF_JUMP(BPF_JMP | BPF_JGE, MEM_ADDR + MEM_SIZE, 4, 0),
        BPF_STMT(BPF_LD  | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ, __NR_read, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ, __NR_write, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = sizeof(filter) / sizeof(filter[0]),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
        puts("Failed to set seccomp");
        exit(1);
    }
}

void init(){
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main(){
    typedef struct {
        char buffer[40];
        char size[16];
    } stack_buff;
    stack_buff p; // set the stack buffer

    init();
    printf("Write the size of your name: ");
    int sizen = readSize(p.size);
    printf("You chose a name of size %s\n", p.size);
    printf("Write your name: ");
    readString(p.buffer, sizen);
    printf("Hello %s\n", p.buffer);
    char *description = mmap((void *)MEM_ADDR, MEM_SIZE, 
        PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0
    );

    printf("Write a description: ");
    readString(description, 0x50);
    printf("Your description is: %s\n", description);
    printf("Bye\n");

    setSecurity();

    // erase got
    for(int i = 0; i<=10; i++){
        ((long long *)(&stdin)-0xE)[i] = 0;
    }
    return 0;
}