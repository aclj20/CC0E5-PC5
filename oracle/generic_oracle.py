from qiskit import QuantumCircuit
from matplotlib.pyplot import show

def generic_oracle(targets: set[str]) -> QuantumCircuit:
    """
    Marca uno o varios estados objetivo con fase negativa.

    Args:
        targets (set[str]): Conjunto de cadenas binarias (por ejemplo: {"0101", "1010"})
                            que representan los estados a marcar.

    Returns:
        qc: Circuito cuántico que implementa el oráculo.
    """
    n_qubits = len(next(iter(targets)))  # Determina cuántos qubits se necesitan
    qc = QuantumCircuit(n_qubits, name="Oracle")  # Crea un circuito cuántico con ese número de qubits

    for target in targets:
        # Invertir la cadena binaria porque Qiskit usa orden little-endian (los bits se leen al revés)
        target = target[::-1]

        # Aplicar compuertas X donde el bit sea 0
        # Esto transforma el estado deseado (como 0101) en |1111⟩ para poder usar una compuerta multicontrolada
        for i, bit in enumerate(target):
            if bit == "0":
                qc.x(i)  # Aplica compuerta X (NOT)

        # Simular una compuerta Z multicontrolada (MCZ)

        # Paso 1: Hadamard al último qubit
        qc.h(n_qubits - 1)

        # Paso 2: Aplicar compuerta multicontrolada X (MCX)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)

        # Paso 3: Hadamard nuevamente al último qubit (completa la MCZ)
        qc.h(n_qubits - 1)

        # Revertir las compuertas X aplicadas antes (volver al estado original)
        for i, bit in enumerate(target):
            if bit == "0":
                qc.x(i)

    return qc  # Devuelve el circuito construido

# Ejemplo de uso: marcar los estados 0101 y 0100
qc = generic_oracle({"0101", "0100"})
qc.draw("mpl")  # Dibuja el circuito
show()  # Muestra el circuito
