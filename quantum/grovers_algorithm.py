from qiskit import QuantumCircuit as qc, QuantumRegister as qr, transpile
from qiskit_aer import AerSimulator
from qiskit.result import Counts
from matplotlib.pyplot import show, subplots, xticks, yticks
from math import pi, sqrt
from heapq import nlargest

# Importamos los oráculos definidos (genérico y XOR)
from oracle.generic_oracle import generic_oracle
from oracle.xor_oracle import xor_oracle

class GroversAlgorithm:
    def __init__(self,
                 oracle_type: str = "generic",  # "generic" o "xor"
                 n_qubits: int = 5,
                 search: set[int] = {3},        # Estado(s) objetivo para el oráculo genérico
                 plaintext: str = "",           # Texto plano para oráculo XOR
                 ciphertext: str = "",          # Texto cifrado para oráculo XOR
                 shots: int = 1000,             # Número de ejecuciones del circuito
                 fontsize: int = 10,            
                 print: bool = False,           # Mostrar circuito en consola
                 combine_states: bool = False   # Agrupar estados no ganadores en Others
                 ) -> None:

        # Guardamos todos los parámetros como atributos
        self.oracle_type = oracle_type
        self.n_qubits = n_qubits
        self.search = search
        self.shots = shots
        self.fontsize = fontsize
        self.print_circuit = print
        self.combine_states = combine_states

        self.plaintext = plaintext
        self.ciphertext = ciphertext

        # Convertimos los números objetivo a binario con ceros a la izquierda
        self._targets = {f"{s:0{n_qubits}b}" for s in self.search}
        self._qubits = qr(self.n_qubits, "qubit")  # Registro cuántico

    # Método para imprimir el circuito si está activado el flag 'print'
    def _print_circuit(self, circuit: qc, name: str) -> None:
        print(f"\n{name}:\n{circuit}")

    # Devuelve el oráculo según el tipo seleccionado
    def _oracle(self) -> qc:
        if self.oracle_type == "xor":
            return xor_oracle(self.plaintext, self.ciphertext)
        return generic_oracle(self._targets)

    # Construye el difusor (inversión sobre la media)
    def _diffuser(self) -> qc:
        qc_diff = qc(self.n_qubits, name="Diffuser")

        # Secuencia estándar de Grover para amplificar el estado marcado
        qc_diff.h(range(self.n_qubits))
        qc_diff.x(range(self.n_qubits))
        qc_diff.h(self.n_qubits - 1)
        qc_diff.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
        qc_diff.h(self.n_qubits - 1)
        qc_diff.x(range(self.n_qubits))
        qc_diff.h(range(self.n_qubits))

        return qc_diff

    # Construye el circuito completo de Grover
    def _grover(self) -> qc:
        circuit = qc(self._qubits, name="Grover Circuit")

        # Inicializamos los qubits en superposición
        circuit.h(self._qubits)
        circuit.barrier()

        # Calculamos número óptimo de iteraciones
        iterations = (pi / 4) * sqrt(2 ** self.n_qubits)
        if self.oracle_type == "generic":
            iterations = (pi / 4) * sqrt((2 ** self.n_qubits) / len(self._targets))

        # Aplicamos oráculo + difusor repetidamente
        for _ in range(int(iterations)):
            circuit.append(self._oracle(), list(range(self.n_qubits)))
            circuit.append(self._diffuser(), list(range(self.n_qubits)))

        # Medición de todos los qubits
        circuit.measure_all()

        # Si está activado, mostramos el circuito en consola
        if self.print_circuit:
            self._print_circuit(circuit, "GROVER CIRCUIT")

        return circuit

    # Imprime por consola el resultado más frecuente
    def _outcome(self, counts: Counts) -> None:
        most_frequent = max(counts, key=counts.get)
        freq = counts[most_frequent]
        print("\nGANADOR:")
        print(f"Binario = {most_frequent} | Decimal = {int(most_frequent, 2)}")
        print(f"Frecuencia = {freq} / {sum(counts.values())} ({freq / sum(counts.values()):.2%})")

        if self.oracle_type == "generic":
            print("\nOBJETIVO(S):")
            print(f"Binario = {self._targets} | Decimal = {self.search}")

    # Muestra un histograma de los resultados
    def _show_histogram(self, histogram_data) -> None:
        winners = {w: histogram_data[w] for w in nlargest(1, histogram_data, key=histogram_data.get)}
        self._outcome(histogram_data)

        x_winners = [*winners]
        y_winners = [*winners.values()]

        # Agrupar los estados no ganadores
        others = {k: v for k, v in histogram_data.items() if k not in winners}
        x_others = "Others" if self.combine_states else list(others)
        y_others = [sum(others.values())] if self.combine_states else list(others.values())

        # Crear gráfico de barras
        fig, ax = subplots(num="Grover's Algorithm — Results", layout="constrained")
        ax.bar(x_winners, y_winners, color="green", label="Objetivo")
        ax.bar(x_others, y_others, color="red", label="Otros")
        ax.legend(fontsize=self.fontsize)
        ax.grid(axis="y", ls="dashed")
        ax.set_axisbelow(True)
        ax.set_title(f"Resultado de {self.shots} Simulaciones", fontsize=int(self.fontsize * 1.45))
        ax.set_xlabel("Estados (Qubits)", fontsize=int(self.fontsize * 1.3))
        ax.set_ylabel("Frecuencia", fontsize=int(self.fontsize * 1.3))
        xticks(fontsize=self.fontsize, family="monospace", rotation=0 if self.combine_states else 70)
        yticks(fontsize=self.fontsize, family="monospace")

        # Mostrar el valor al pasar el mouse
        annotation = ax.annotate("",
                                 xy=(0, 0),
                                 xytext=(5, 5),
                                 xycoords="data",
                                 textcoords="offset pixels",
                                 ha="center", va="bottom",
                                 family="monospace", weight="bold",
                                 fontsize=self.fontsize,
                                 bbox=dict(facecolor="white", alpha=0.4, edgecolor="None", pad=0))

        def _hover(event):
            visible = annotation.get_visible()
            if event.inaxes == ax:
                for bars in ax.containers:
                    for bar in bars:
                        cont, _ = bar.contains(event)
                        if cont:
                            x = bar.get_x() + bar.get_width() / 2
                            y = bar.get_y() + bar.get_height()
                            annotation.xy = (x, y)
                            annotation.set_text(y)
                            annotation.set_visible(True)
                            fig.canvas.draw_idle()
                            return
            if visible:
                annotation.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", _hover)
        show()

    # Ejecuta el algoritmo completo
    def run(self) -> None:
        backend = AerSimulator(method="density_matrix")  # Seleccionamos el simulador
        transpiled = transpile(self._grover(), backend, optimization_level=2)  
        job = backend.run(transpiled, shots=self.shots)  # Ejecutamos el circuito
        result = job.result()
        data = result.get_counts()  # Recolectamos los resultados
        self._show_histogram(data)  # Mostramos el histograma


if __name__ == "__main__":
    # Para usar el oráculo genérico:
    # GroversAlgorithm(oracle_type="generic", n_qubits=4, search={3}, print=True).run()

    # Para usar el oráculo XOR:
    GroversAlgorithm(
        oracle_type="xor",
        plaintext="00011",
        ciphertext="11100",
        n_qubits=5,
        print=True
    ).run()