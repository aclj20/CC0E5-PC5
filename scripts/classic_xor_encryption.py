"""
xor_cipher_bin.py

Cifra un mensaje binario aleatorio con una clave binaria aleatoria utilizando XOR,
ambos de longitud especificada por el usuario, y guarda los resultados en archivos binarios.
La semilla de aleatoriedad puede establecerse, permitiendo reproducibilidad entre ejecuciones.

Este script genera un mensaje y una clave aleatoria de `n` bits, los almacena como archivos binarios,
realiza la operación XOR entre ellos y guarda el resultado como archivo binario de ciphertext.

Uso
---
En consola, ejecuta:

    python xor_cipher_bin.py

Parámetros opcionales
---------------------
--message_file : str
    Nombre del archivo de salida para el mensaje. Por defecto, "message.bin".
--key_file : str
    Nombre del archivo de salida para la clave. Por defecto, "key.bin".
--ciphertext_file : str
    Nombre del archivo de salida para el ciphertext. Por defecto, "ciphertext.bin".
--seed : int
    Semilla de aleatoriedad para generar los bits. Por defecto, None (aleatorio)
-n, --n_bits : int
    Número de bits para el mensaje y la clave (ej. 8, 16, 32...). Por defecto, 16

Ejemplo
-------
    python xor_cipher_bin.py -n 16

Esto generará tres archivos binarios en el directorio "bins": `message.bin`, `key.bin` y `ciphertext.bin`,
cada uno con 2 bytes (16 bits) de información aleatoria o cifrada. Los bits generados serán aleatorios.

Notas
-----
- Si `n` no es múltiplo de 8, se utiliza el número mínimo de bytes suficientes para contener los bits.

Requisitos
----------
- Python 3.x

Autor
-----
Diego Akira García Rojas
"""

import os
import sys
import argparse
import random


def generate_random_bytes(n_bits):
    """
    Genera una cadena de bytes aleatorios suficiente para cubrir n_bits.

    Parameters
    ----------
    n_bits : int
        Número de bits a cubrir.

    Returns
    -------
    bytes
        Cadena de bytes aleatorios.
    """
    n_bytes = (n_bits + 7) // 8
    return os.urandom(n_bytes)


def generate_random_bytes_with_seed(n_bits, seed):
    """
    Genera bytes aleatorios de manera reproducible usando una semilla.

    Parameters
    ----------
    n_bits : int
        Número de bits a cubrir.
    seed : int
        Semilla para el generador aleatorio.

    Returns
    -------
    bytes
        Bytes pseudoaleatorios reproducibles.
    """
    n_bytes = (n_bits + 7) // 8
    rnd = random.Random(seed)
    return bytes([rnd.getrandbits(8) for _ in range(n_bytes)])


def save_bytes_to_file(filename, data):
    """
    Guarda datos binarios en un archivo.

    Parameters
    ----------
    filename : str
        Ruta del archivo de salida.
    data : bytes
        Datos a escribir.
    """
    with open(filename, "wb") as f:
        f.write(data)


def load_bytes_from_file(filename):
    """
    Carga datos binarios desde un archivo.

    Parameters
    ----------
    filename : str
        Ruta del archivo a leer.

    Returns
    -------
    bytes
        Datos leídos.
    """
    with open(filename, "rb") as f:
        return f.read()


def xor_bytes(data1, data2):
    """
    Realiza una operación XOR byte a byte entre dos secuencias de bytes.

    Parameters
    ----------
    data1 : bytes
        Primer operando.
    data2 : bytes
        Segundo operando.

    Returns
    -------
    bytes
        Resultado del XOR byte a byte.
    """
    return bytes([b1 ^ b2 for b1, b2 in zip(data1, data2)])


def main():
    """
    Función principal. Genera archivos binarios para mensaje, clave y texto cifrado
    usando cifrado XOR.

    Lee los argumentos de línea de comandos y ejecuta las funciones principales.
    """
    parser = argparse.ArgumentParser(
        description="Cifrado XOR de archivos binarios con clave aleatoria."
    )
    parser.add_argument(
        "-n",
        "--n_bits",
        type=int,
        default=16,
        help="Número de bits para mensaje y clave (ej. 8, 16, 32...)",
    )
    parser.add_argument(
        "--message_file",
        default="bins/message.bin",
        help="Archivo para guardar el mensaje",
    )
    parser.add_argument(
        "--key_file", default="bins/key.bin", help="Archivo para guardar la clave"
    )
    parser.add_argument(
        "--ciphertext_file",
        default="bins/ciphertext.bin",
        help="Archivo para el texto cifrado",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semilla para el generador aleatorio (opcional, para reproducibilidad)",
    )
    args = parser.parse_args()

    n_bits = args.n_bits

    if args.seed is not None:
        message = generate_random_bytes_with_seed(n_bits, args.seed)
        key = generate_random_bytes_with_seed(
            n_bits, args.seed + 1
        )  # Usa semilla distinta para clave
    else:
        message = generate_random_bytes(n_bits)
        key = generate_random_bytes(n_bits)

    # Guarda ambos archivos
    save_bytes_to_file(args.message_file, message)
    save_bytes_to_file(args.key_file, key)

    # Aplica XOR bit a bit
    ciphertext = xor_bytes(message, key)
    save_bytes_to_file(args.ciphertext_file, ciphertext)

    print(f"Mensaje aleatorio guardado en {args.message_file}: {message.hex()}")
    print(f"Clave aleatoria guardada en {args.key_file}: {key.hex()}")
    print(f"Ciphertext guardado en {args.ciphertext_file}: {ciphertext.hex()}")


if __name__ == "__main__":
    main()
