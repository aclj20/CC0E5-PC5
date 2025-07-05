"""
brute_xor_decryption.py

Realiza ataque de fuerza bruta aleatorio sobre un ciphertext cifrado por XOR.
Intenta claves aleatorias (sin repetición) hasta encontrar el mensaje original.
Retorna el número de intentos realizados y la clave encontrada.

Uso
---
    python brute_xor_decryption.py --ciphertext_file <archivo> --plaintext_file <archivo>

Parámetros opcionales
---------------------
--n_bits : int
    Número de bits de clave a explorar. Si no se especifica, se usa el tamaño del archivo.
--seed : int
    Semilla para el generador aleatorio (para reproducibilidad).
--ciphertext_file : str
    Archivo binario del texto cifrado. Por defecto bins/ciphertext.bin
--plaintext_file : str
    Archivo binario del mensaje original. Por defecto bins/message.bin

Ejemplo
-------
    python random_bruteforce_xor.py --ciphertext_file bins/ciphertext.bin --plaintext_file bins/message.bin --seed 42

Notas
-----
- El ataque es aleatorio, por lo que el número de intentos varía en cada ejecución.
- Solo recomendado para claves pequeñas (<24 bits).

Requisitos
----------
- Python 3.x

Autor
-----
Diego Akira García Rojas (Akira-13)
"""

import os
import argparse
import random


def load_bytes_from_file(filename):
    """Carga datos binarios desde un archivo."""
    with open(filename, "rb") as f:
        return f.read()


def xor_bytes(data, key_bytes):
    """Aplica XOR entre datos y una clave de igual longitud."""
    return bytes([b ^ k for b, k in zip(data, key_bytes)])


def int_to_bytes(i, length):
    """Convierte un entero a bytes de longitud `length` (big endian)."""
    return i.to_bytes(length, byteorder="big")


def main():
    parser = argparse.ArgumentParser(
        description="Fuerza bruta aleatoria de ciphertext XOR."
    )
    parser.add_argument(
        "--ciphertext_file",
        default="bins/ciphertext.bin",
        help="Archivo binario del ciphertext.",
    )
    parser.add_argument(
        "--plaintext_file",
        default="bins/message.bin",
        help="Archivo binario del mensaje original.",
    )
    parser.add_argument(
        "--n_bits",
        type=int,
        default=None,
        help="(Opcional) Número de bits de clave a explorar.",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Semilla para el generador aleatorio."
    )
    args = parser.parse_args()

    ciphertext = load_bytes_from_file(args.ciphertext_file)
    plaintext = load_bytes_from_file(args.plaintext_file)
    file_bytes = len(ciphertext)
    full_n_bits = file_bytes * 8

    n_bits = args.n_bits if args.n_bits is not None else full_n_bits
    n_bytes = (n_bits + 7) // 8

    if n_bits > full_n_bits:
        raise ValueError(
            f"n_bits ({n_bits}) no puede ser mayor al tamaño del archivo ({full_n_bits} bits)."
        )

    num_keys = 2**n_bits

    if num_keys > 2**24:
        print(
            "! Advertencia: El espacio de claves es muy grande. Solo recomendado para claves <=24 bits."
        )

    # Inicializa generador aleatorio
    rng = random.Random(args.seed)
    tried = set()
    attempts = 0

    print(
        f"Buscando la clave original por fuerza bruta aleatoria en un espacio de {num_keys} claves posibles..."
    )

    while True:
        key = rng.randrange(num_keys)
        if key in tried:
            continue  # Ya intentada
        tried.add(key)
        key_bytes = int_to_bytes(key, n_bytes)
        # Rellena la clave a la izquierda con ceros si es menor que el archivo
        if len(key_bytes) < file_bytes:
            key_bytes = (b"\x00" * (file_bytes - len(key_bytes))) + key_bytes
        if len(key_bytes) > file_bytes:
            key_bytes = key_bytes[-file_bytes:]
        candidate_message = xor_bytes(ciphertext, key_bytes)
        attempts += 1
        if candidate_message == plaintext:
            print(f"¡Clave encontrada!: {key:0{n_bits}b}")
            print(f"Intentos realizados: {attempts}")
            print(f"Clave en hexadecimal: {key_bytes.hex()}")
            break
        if attempts % 10000 == 0:
            print(f"{attempts} intentos realizados...")


if __name__ == "__main__":
    main()
