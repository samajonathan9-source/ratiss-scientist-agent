/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

// Custom Base44 implementation for RATISS obfuscation
// Using a custom character set to differentiate from standard Base64
const ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"; // 44 characters

export function encodeBase44(str: string): string {
  let num = BigInt('0x' + Buffer.from(str).toString('hex'));
  let encoded = "";
  while (num > 0n) {
    encoded = ALPHABET[Number(num % 44n)] + encoded;
    num = num / 44n;
  }
  return encoded;
}

export function decodeBase44(encoded: string): string {
  let num = 0n;
  for (let i = 0; i < encoded.length; i++) {
    num = num * 44n + BigInt(ALPHABET.indexOf(encoded[i]));
  }
  let hex = num.toString(16);
  if (hex.length % 2 !== 0) hex = '0' + hex;
  return Buffer.from(hex, 'hex').toString();
}
