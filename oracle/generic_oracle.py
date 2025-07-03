from qiskit import QuantumCircuit
from matplotlib.pyplot import show

def generic_oracle(targets: set[str]) -> QuantumCircuit:
    """Mark target state(s) with negative phase.

        Args:
            targets (set[str]): N-qubit binary string(s) representing target state(s).

        Returns:
            qc: Quantum circuit representation of oracle.
        """
    n_qubits = len(next(iter(targets)))
    # Create N-qubit quantum circuit for oracle
    qc = QuantumCircuit(n_qubits, name="Oracle")

    for target in targets:
        # Reverse target state since Qiskit uses little-endian for qubit ordering
        target = target[::-1]
        # Flip zero qubits in target
        for i, bit in enumerate(target):
            if bit == "0":
                # Pauli-X gate
                qc.x(i)
        
        # Simulate (N - 1)-control Z gate
        # 1. Hadamard gate
        qc.h(n_qubits - 1)

        # 2. (N - 1)-control Toffoli gate
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)

        # 3. Hadamard gate
        qc.h(n_qubits - 1)
        # Flip back to original state
        for i, bit in enumerate(target):
            if bit == "0":
                # Pauli-X gate
                qc.x(i)
    return qc

qc = generic_oracle({"0101", "0100"})
qc.draw("mpl")
show()