from qiskit.circuit import QuantumRegister, QuantumCircuit
from matplotlib.pyplot import show

def xor_oracle(plaintext: str, ciphertext: str, insert_barriers: bool = True)  -> QuantumCircuit:
    assert len(plaintext) == len(ciphertext), "La longitud del texto plano y del texto cifrado debe ser la misma"
    n_qubits = len(plaintext)

    # La clave es de tamaño n_qubits
    qc = QuantumCircuit(n_qubits, name="Oracle")

    # Debemos comprobar si la clave XOR con el texto plano es igual al texto cifrado (key XOR plaintext = ciphertext)

    # Primero, calculamos la clave XOR con el texto plano, lo cual se hace usando compuertas X
    for index, bit in enumerate(plaintext[::-1]): # [::-1] para cumplir con el formato little-endian de Qiskit
        if bit == "1":
            qc.x(index)

    # Aplicamos una barrera para una mejor visualización
    if insert_barriers: 
        qc.barrier()

    # Ahora queremos invertir (marcar) el estado si es igual al texto cifrado (ciphertext)
    # Una compuerta Z controlada por n qubits (C^n-Z) invertirá la fase solo si todos los qubits están en 1
    # Por lo tanto, solo necesitamos aplicar compuertas X en los qubits que deberían ser 0 en el ciphertext


    for index, bit in enumerate(ciphertext[::-1]): # [::-1] para cumplir con el formato little-endian de Qiskit
        if bit == "0":
            qc.x(index)

    # Aplicamos una barrera para una mejor visualización
    if insert_barriers:
        qc.barrier()


    # Aplicar la compuerta MCZ usando MCX
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), [n_qubits - 1])
    qc.h(n_qubits - 1)

    if insert_barriers: 
        qc.barrier()

    # Revertir las compuertas X aplicadas antes para volver al estado original

    for index, bit in enumerate(ciphertext[::-1]): 
        if bit == "0":
            qc.x(index)

    if insert_barriers: 
        qc.barrier()

    for index, bit in enumerate(plaintext[::-1]): 
        if bit == "1":
            qc.x(index)

    return qc

qc = xor_oracle("0101", "0100")
qc.draw("mpl")
show()