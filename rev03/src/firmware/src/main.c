#include <stdio.h>
#include <stdint.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/base64.h>

#include <atca_basic.h>

#include "secrets.h"

int main(void)
{
	char banner_starting_boctf[] = {
		'.', 'S', 't', 'a', 'r', 't', 'i', 'n', 'g', ' ', 'U',
		'l', 'i', 's', 's', 'e', 'C', 'T', 'F', ' ', 'o', 'n',
		' ', 'E', 'S', 'P', '3', '2', '-', 'W', 'R', 'O', 'O',
		'M', '-', 'A', 'T', 'E', 'C', 'C', '6', '0', '8', 'A',
		'\x0'
	};
	ATCAIfaceCfg cfg = cfg_ateccx08a_i2c_default;
	int status = 0;
	int is_verified = 0;
	uint16_t key_id = ATCA_TEMPKEY_KEYID; 
	atca_aes_gcm_ctx_t ctx;

	uint8_t iv[12] = SECRET_IV;
	uint8_t tag[16] = SECRET_TAG;
	uint8_t key[32] = SECRET_KEY;

	uint8_t encrypted_flag[] = SECRET_FLAG;
	uint8_t plaintext[] = SECRET_FLAG;
	printf("%s\n", banner_starting_boctf);

	cfg.cfg_data = "i2c0";
	cfg.atcai2c.bus = 0;
	cfg.atcai2c.address = 0xc0;

	status = atcab_init(&cfg);
	printf("status: %d\n", status);
	status = atcab_wakeup();
	printf("status: %d\n", status);
	status = atcab_nonce_load(NONCE_MODE_TARGET_TEMPKEY, key, ATCA_KEY_SIZE);
	printf("status: %d\n", status);

	status = atcab_aes_gcm_init(&ctx, key_id, 0, iv, AES_DATA_SIZE - 4);
	printf("status: %d\n", status);
	status = atcab_aes_gcm_decrypt_update(&ctx, encrypted_flag, SECRET_FLAG_LEN, plaintext);
	printf("status: %d\n", status);
	status = atcab_aes_gcm_decrypt_finish(&ctx, tag, 16, &is_verified);
	printf("status: %d\n", status);

	printf("verified: %d\n", is_verified);
	printf("flag: %s\n", plaintext);

	k_panic();
	return 0;
}

