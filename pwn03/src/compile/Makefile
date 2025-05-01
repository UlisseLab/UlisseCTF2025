CFLAGS=--sysroot=/opt/cheri/output/rootfs-riscv64
CC=/opt/cheri/output/sdk/bin/riscv64-unknown-freebsd-clang
STRIP=/opt/cheri/output/sdk/bin/riscv64-unknown-freebsd-strip

all: cheri-challenge

%: %.c
	        $(CC) $(CFLAGS) -o $@ $<
		$(STRIP) $@



