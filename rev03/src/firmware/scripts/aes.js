#!/usr/bin/env node
const fs = require('node:fs');
const crypto = require('crypto');

function decrypt(key, iv, tag, ciphertext) {
    var decipher = crypto.createDecipheriv('aes-128-gcm', key, iv);
    decipher.setAuthTag(tag);
    var decrypted = decipher.update(ciphertext);
    decrypted += decipher.final('utf8');
    return decrypted;
}
    

function encrypt(key, iv, plaintext, fciphertext, ftag) {
    var cipher = crypto.createCipheriv('aes-128-gcm', key, iv);
    var encrypted = cipher.update(plaintext, 'utf8');
    cipher.final()
    fs.writeFileSync(fciphertext, encrypted);
    var authTag = cipher.getAuthTag()
    fs.writeFileSync(ftag, authTag);
}

let key = fs.readFileSync(process.argv[3]);
let iv = fs.readFileSync(process.argv[4]);

if (process.argv[2] === 'encrypt') {
    let payload = fs.readFileSync(process.argv[5]);
    encrypt(key, iv, payload, process.argv[6], process.argv[7])
} else if (process.argv[2] === 'decrypt') {
    let tag = fs.readFileSync(process.argv[5]);
    let ciphertext = fs.readFileSync(process.argv[6]);
    console.log(decrypt(key, iv, tag, ciphertext))
} else {
    console.log("Unsupported action ", process.argv[2]);
}
