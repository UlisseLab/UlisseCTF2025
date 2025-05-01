#!/bin/bash

set -eux

MEMORY=8192
SSH_PORT=10022

execute_qemu() {
	qemu-system-riscv64cheri \
		-serial unix:console.sock,server,nowait \
		-nographic \
		-drive file=/opt/cheri/output/cheribsd-riscv64-purecap.qcow2,format=qcow2,if=virtio \
		-machine virt \
		-kernel /opt/cheri/output/rootfs-riscv64-purecap/boot/kernel/kernel \
		-m $MEMORY \
		-cpu rv64 \
		-smp 1 \
		-netdev user,id=u1,hostfwd=tcp:127.0.0.1:10022-:22 \
		-device virtio-net-device,netdev=u1,bus=virtio-mmio-bus.2 \
		;
}

ssh_command() {
	ssh -p $SSH_PORT -oStrictHostKeyChecking=false -i id_ed25519 root@localhost $@
}

update_vm() {
	# generate ssh key
	rm -f id_ed25519{,.pub}
	ssh-keygen -f id_ed25519 -t ed25519 -N ''
	# Wait for machine to be available
	while ! ( sleep 5 | socat - TCP:localhost:$SSH_PORT ) | grep -m 1 SSH; do
		sleep 1
	done
	# Login over terminal and install ssh key
	(echo "exit" ; sleep 10; echo "exit"; sleep 10 ; echo "root"; sleep 10) | socat - unix:console.sock
	sleep 5
	(echo "" ; sleep 3 ; echo "mkdir -p .ssh"; sleep 1; echo "echo $(cat id_ed25519.pub) > .ssh/authorized_keys"; sleep 1;) | socat - unix:console.sock
	# Finally, login via SSH
	ssh_command "echo '$FLAG' > /flag.txt"
	ssh_command "chmod 444 /flag.txt"
	ssh_command 'mkdir /usr/local/bin'
	scp -oStrictHostKeyChecking=false -P $SSH_PORT -i id_ed25519 /challenge/attachments/cheri-challenge root@localhost:/usr/local/bin/cheri-challenge
	# Change login password to unguessable one
	ssh_command "chpass -p '$PASSWORD'"
	ssh_command "chpass -p '$PASSWORD' toor"
	ssh_command "truncate -s 0 /etc/motd"
	ssh_command "echo user:1000::::::/home/user:/bin/sh | adduser -w random -f /dev/stdin"
	ssh_command "mkdir /home/user/.ssh"
	ssh_command "chown user:user /home/user/.ssh"
	ssh_command "chmod 0700 /home/user/.ssh"
	ssh_command "cp /root/.ssh/authorized_keys /home/user/.ssh/authorized_keys"
	ssh_command "chown user:user /home/user/.ssh/authorized_keys"
	ssh_command "mount -f -u -o ro /"
	socat TCP-LISTEN:$PORT,fork exec:"ssh -oStrictHostKeyChecking=false -i id_ed25519 -p $SSH_PORT user@localhost /usr/local/bin/cheri-challenge"
}
cd $HOME

execute_qemu &
update_vm
sleep 10000000
