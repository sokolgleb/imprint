import base64
import os
from typing import Optional

from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class StegoCryptController:

    def _generate_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _encrypt_text(self, text: str, password: str) -> tuple[bytes, bytes]:
        salt = os.urandom(16)
        key = self._generate_key(password, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(text.encode("utf-8"))
        return salt, encrypted_data

    def _decrypt_text(self, encrypted_data: bytes, salt: bytes, password: str) -> str:
        key = self._generate_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode("utf-8")

    def prepare_data(self, text: str, password: str = None) -> bytes:
        text_bytes = text.encode("utf-8")

        if password:
            salt = os.urandom(16)
            key = self._generate_key(password, salt)
            f = Fernet(key)
            encrypted_data = f.encrypt(text_bytes)

            flag = b"\x01"
            data_len = len(encrypted_data).to_bytes(4, "big")
            return flag + data_len + salt + encrypted_data
        else:
            flag = b"\x00"
            data_len = len(text_bytes).to_bytes(4, "big")
            dummy_salt = b"\x00" * 16
            return flag + data_len + dummy_salt + text_bytes

    def encode(self, image: Image, text: str, password: Optional[str] = None) -> Image:
        data = self.prepare_data(text, password)

        pixels = list(image.getdata())

        data_bits = "".join(f"{b:08b}" for b in data)
        data_len = len(data_bits)

        if data_len > len(pixels) * 3:
            raise ValueError("Слишком много данных для этого изображения!")

        new_pixels = []
        bit_index = 0

        for r, g, b, a in pixels:
            if bit_index < data_len:
                r = (r & ~1) | int(data_bits[bit_index])
                bit_index += 1
            if bit_index < data_len:
                g = (g & ~1) | int(data_bits[bit_index])
                bit_index += 1
            if bit_index < data_len:
                b = (b & ~1) | int(data_bits[bit_index])
                bit_index += 1

            new_pixels.append((r, g, b, a))
            if bit_index >= data_len:
                break

        new_pixels.extend(pixels[len(new_pixels) :])

        stegano_image = Image.new("RGB", image.size)
        stegano_image.putdata(new_pixels)

        return stegano_image

    def _decode(self, image: Image, data_len_bytes: int) -> bytes:
        pixels = image.getdata()

        extracted_bits = []
        bits_to_extract = data_len_bytes * 8

        for r, g, b in pixels:
            if len(extracted_bits) < bits_to_extract:
                extracted_bits.append(str(r & 1))
            if len(extracted_bits) < bits_to_extract:
                extracted_bits.append(str(g & 1))
            if len(extracted_bits) < bits_to_extract:
                extracted_bits.append(str(b & 1))
            if len(extracted_bits) >= bits_to_extract:
                break

        byte_chunks = [
            "".join(extracted_bits[i : i + 8]) for i in range(0, bits_to_extract, 8)
        ]
        extracted_data = bytes([int(chunk, 2) for chunk in byte_chunks])

        return extracted_data

    def decode(self, image: Image, password: str = None) -> str:
        header = self._decode(image, 21)
        is_encrypted = header[0] == 0x01
        data_len = int.from_bytes(header[1:5], "big")
        salt = header[5:21]

        total_data = self._decode(image, 21 + data_len)
        payload = total_data[21:]

        if is_encrypted:
            if not password:
                raise ValueError("Password mismatch")
            return self._decrypt_text(payload, salt, password)
        else:
            return payload.decode("utf-8")
