#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#include <sys/mman.h>

static void *btpmem;
static size_t btpsize;

static void btpinit(void)
{
    btpsize = 0x100000;
    btpmem = mmap(NULL, btpsize, PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANON, -1, 0);
}

void *btpmalloc(size_t size)
{
    void *alloc;
    size_t allocsize;

    if (btpmem == NULL)
        btpinit();

    alloc = btpmem;
    /* RISC-V ABIs require 16-byte alignment */
    allocsize = __builtin_align_up(size, 16);

#if defined(__CHERI_PURE_CAPABILITY__) && !defined(CHERI_NO_ALIGN_PAD)
    allocsize = cheri_representable_length(allocsize);
    alloc = __builtin_align_up(alloc,
        ~cheri_representable_alignment_mask(allocsize) + 1);
    allocsize += (char *)alloc - (char *)btpmem;
#endif

    if (allocsize > btpsize)
        return (NULL);

    btpmem = (char *)btpmem + allocsize;
    btpsize -= allocsize;
#ifdef __CHERI_PURE_CAPABILITY__
    alloc = cheri_bounds_set(alloc, size);
#endif
    return (alloc);
}

void btpfree(void *ptr)
{
    (void)ptr;
}

void my_shell(void)
{
	system("/bin/sh");
}

static char *gets(char *s) {
        int i = 0;
        char c = fgetc(stdin);
        while (c != '\x00' && c != '\n') {
                s[i++] = c;
        }
	s[i++] = '\x00';
        return s;
}

// Not vulnerable due to cheri protections (fat pointers)
static void vulnerable1() {
        unsigned int v;
        unsigned char *vla = NULL;
        printf("Evolution requires a size to build a VLA\n");
        scanf("%d", &v);
        vla = alloca(v);
        printf("Evolution requires a string\n");
        scanf("%s", vla);
}

// Not vulnerable due to cheri protections (fat pointers)
static void vulnerable2() {
        unsigned int v;
        unsigned char *vla = NULL;
        printf("Evolution requires a size to build an array\n");
        scanf("%d", &v);
        vla = malloc(v);
        printf("Evolution requires a string\n");
        scanf("%s", vla);
        free(vla);
}

// Not vulnerable due to cheri protections (fat pointers)
static void vulnerable3() {
        unsigned long long *k;
        unsigned long long v;
        printf("Evolution requires a pointer\n");
        scanf("%llu", (unsigned long long *) &k);
        printf("Evolution requires a value to write\n");
        scanf("%llu", (unsigned long long *) &v);
        *k = v;
        ((void (*)(void))v)();
}

// This is the intended vulnerable function
static void vulnerable4() {
        // This structure gets allocated on the heap
        struct x {
                int key;
                // This pointer is not protected by cheri due to its building
                void (*value)(void);
        };
        struct x *v = btpmalloc(sizeof(struct x));
        printf("Evolution requires a string\n");
        scanf("%s", (char *) &v);
#if 1
	v->value = my_shell;
#endif
        // Therefore this entrypoint is not protected
        v->value();
}

// Same as vulnerable1 but more interesting due to the use of gets :D
static void vulnerable5() {
        unsigned int v;
        char *vla = NULL;
        printf("Evolution requires a size to build a VLA\n");
        scanf("%d", &v);
        vla = alloca(v);
        printf("Evolution requires a string\n");
        vla = gets(vla);
}

// Same as vulnerable1 but more interesting due to the use of gets :D
static void vulnerable6() {
        unsigned int v;
        char fmt[32];
        printf("Evolution requires a string to echo it\n");
        scanf("%s", fmt);
        printf(fmt);
}

int main(int argc, char **argv)
{
        char c = 0;
	setvbuf(stdin, (char *)NULL, _IONBF, 0);
	setvbuf(stdout, (char *)NULL, _IONBF, 0);
	setvbuf(stderr, (char *)NULL, _IONBF, 0);
        printf("Welcome to cheri PWN tutorial!\n");
        printf("\n");
        printf("Choose your vulnerability stone from your backpack!\n");
        printf("\n");
        printf("  1 . Classic Buffer Overflow Berry! ...\n");
        printf("  2 . Classic heap exploitation Berry!  ...\n");
        printf("  3 . Classic memory write procedure Berry! ...\n");
        printf("  4 . Classic Heap object Overflow Berry! ...\n");
        printf("  5 . Forgotten old gets Berry!!! ...\n");
        printf("  6 . Leaking sink berry\n");
        printf("> ");
        fflush(stdout);
        c = fgetc(stdin);
        printf("\n\n");
        printf("What! Your PWN is evolving!\n");
        switch (c) {
                case '1':
                        vulnerable1();
                        break;
                case '2':
                        vulnerable2();
                        break;
                case '3':
                        vulnerable3();
                        break;
                case '4':
                        vulnerable4();
                        break;
                case '5':
                        vulnerable5();
                        break;
                case '6':
                        vulnerable6();
                        break;
                default:
                        printf("Huh? PWN stopped evolving!\n");
                        return 1;
        }
        printf("Congratulations! Your PWN evolved to an invulnerable PWN.\n");

        return 0;
}

