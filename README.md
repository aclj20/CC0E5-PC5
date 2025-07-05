# CC0E5-PC5 - Cryptoparty: Rompiendo cifrados simétricos con el algoritmo de Grover

## Scripts

### `classic_xor_encryption.py`

Genera mensaje, clave y ciphertext aleatorios:

```sh
python3 scripts/classic_xor_encryption.py -n 16 --seed 42
```

**Parámetros principales:**

* `-n, --n_bits`: Número de bits para mensaje y clave (ejemplo: 8, 16, 32, ...).
  *Por defecto: 16*
* `--seed`: Semilla de aleatoriedad para reproducibilidad.
  *Por defecto: None*
* `--message_file`: Nombre del archivo binario para el mensaje.
  *Por defecto: `bins/message.bin`*
* `--key_file`: Nombre del archivo binario para la clave.
  *Por defecto: `bins/key.bin`*
* `--ciphertext_file`: Nombre del archivo binario para el ciphertext.
  *Por defecto: `bins/ciphertext.bin`*

Se generarán archivos binarios en la carpeta indicada con los datos aleatorios y cifrados.

---

### `brute_xor_decryption.py`

Busca la clave correcta probando claves aleatorias (sin repetición) hasta encontrar el mensaje original:

```sh
python3 scripts/brute_xor_decryption.py --ciphertext_file bins/ciphertext.bin --plaintext_file bins/message.bin --seed 42
```

**Parámetros principales:**

* `--ciphertext_file`: Archivo binario del texto cifrado.
  *Por defecto: `bins/ciphertext.bin`*
* `--plaintext_file`: Archivo binario del mensaje original.
  *Por defecto: `bins/message.bin`*
* `--n_bits`: (Opcional) Número de bits de clave a explorar. Si no se indica, se asume tamaño igual al archivo.
* `--seed`: Semilla para el generador aleatorio (reproducibilidad).

El script imprimirá en pantalla:

* Clave encontrada (en binario y hexadecimal)
* Número de intentos realizados

**Notas:**

* El ataque es aleatorio, por lo que el número de intentos puede variar entre ejecuciones.
* **No recomendado para claves mayores a 24 bits** (el tiempo crece exponencialmente).

## Ejemplo de flujo

1. **Generar archivos:**

   ```sh
   python classic_xor_encryption.py -n 16 --seed 123
   ```

   *Esto crea `bins/message.bin`, `bins/key.bin` y `bins/ciphertext.bin`.*

2. **Atacar el ciphertext:**

   ```sh
   python brute_xor_decryption.py --ciphertext_file bins/ciphertext.bin --plaintext_file bins/message.bin --seed 123
   ```


## Notas adicionales

* **Reproducibilidad:**
  Usa el argumento `--seed` en ambos scripts para obtener los mismos resultados entre ejecuciones.
* **Limitar el espacio de clave:**
  Puedes usar el argumento `--n_bits` para atacar solo un subconjunto de posibles claves (útil en pruebas).

## Integrantes

* Diego Akira García Rojas (Akira-13)
* Ariana Camila López Julcarima (aclj20)

## Requisitos

* Python 3.x
