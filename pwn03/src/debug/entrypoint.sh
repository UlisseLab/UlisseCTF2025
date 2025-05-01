#!/bin/bash

set -eu

MEMORY=8192
SSH_PORT=10022

execute_qemu() {
	qemu-system-riscv64cheri \
		-serial unix:console.sock,server,nowait \
		-drive file=/opt/cheri/output/cheribsd-riscv64-purecap.qcow2,format=qcow2,if=virtio \
		-machine virt \
		-kernel /opt/cheri/output/rootfs-riscv64-purecap/boot/kernel/kernel \
		-m $MEMORY \
		-cpu rv64 \
		-smp 1 \
		-netdev user,id=u1,hostfwd=tcp:127.0.0.1:10022-:22,hostfwd=tcp:127.0.0.1:$PORT-:$PORT \
		-device virtio-net-device,netdev=u1,bus=virtio-mmio-bus.2 \
		;
}

ssh_command() {
	ssh -p $SSH_PORT -oHostStrictKeyChecking=false -i id_ed25519 
}

update_vm() {
	# generate ssh key
	rm ./id_ed25519{,.pub}
	ssh-keygen -f ./id_ed25519 -t ed25519 -N ''
	# Wait for machine to be available
	nc localhost $SSH_PORT < /dev/null | grep -m 1 SSH
	# Login over terminal and install ssh key
	(echo "exit" ; sleep 1 ; echo "root"; sleep 1) | socat - unix:console.sock
	sleep 1
	(echo "" ; sleep 1 ; echo "mkdir -p .ssh"; echo "echo $(cat id_ed25519.pub) > .ssh/authorized_keys"; sleep 1;) | socat - unix:console.sock
	# Finally, login via SSH
	# Change login password to unguessable one
	ssh_command chpasswd -p "$PASSWORD"
	ssh_command chpasswd toor -p "$PASSWORD"
	scp -P $SSH_PORT -i id_ed25519 /challenge/attachments/cheri-challenge localhost:/usr/local/bin/cheri-challenge
	ssh_command echo "$FLAG" > /flag.txt
	ssh_command chmod 444 > /flag.txt
	# XXX Socaz?
	ssh_command /bin/su nobody socat TCP-LISTEN:5534,fork exec:/usr/local/bin/cheri-challenge
}

compile_challenge() {
	cd /challenge/src/
	make
}

compile_challenge
execute_qemu &
update_vm
