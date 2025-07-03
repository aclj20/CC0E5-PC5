from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from qiskit import QuantumCircuit as qc
from qiskit import QuantumRegister as qr
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.result import Counts
from matplotlib.pyplot import show, subplots, xticks, yticks
from math import pi, sqrt
from heapq import nlargest
from oracle.generic_oracle import generic_oracle
class GroversAlgorithm:
    def __init__(self,
                 title: str = "Grover's Algorithm",
                 n_qubits: int = 5,
                 search: set[int] = { 11, 9, 0, 3 },
                 shots: int = 1000,
                 fontsize: int = 10,
                 print: bool = False,
                 combine_states: bool = False) -> None:
        """
        Simulate Grover's algorithm using Qiskit's AerSimulator.

        Args:
            title (str, optional): Window title. Defaults to "Grover's Algorithm".
            n_qubits (int, optional): Number of qubits. Defaults to 5.
            search (set[int], optional): Set of nonnegative integers to search for using Grover's algorithm. Defaults to { 11, 9, 0, 3 }.
            shots (int, optional): Amount of times the algorithm is simulated. Defaults to 10000.
            fontsize (int, optional): Histogram's font size. Defaults to 10.
            print (bool, optional): Whether or not to print quantum circuit(s). Defaults to False.
            combine_states (bool, optional): Whether to combine all non-winning states into 1 bar labeled "Others" or not. Defaults to False.
        """
        self.title = title
        self.n_qubits = n_qubits
        self.shots = shots
        self.fontsize = fontsize
        self.print_circuit = print
        self.combine_states = combine_states

        # Set of nonnegative ints to search for
        self.search: set[int] = set(search)

        # Set of m N-qubit binary strings representing target state(s) (i.e. self.search in base 2)
        self._targets: set[str] = { f"{s:0{self.n_qubits}b}" for s in self.search }
        
        # N-qubit quantum register
        self._qubits: qr = qr(self.n_qubits, "qubit")

    def _print_circuit(self, circuit: qc, name: str) -> None:
        """Print quantum circuit.

        Args:
            circuit (qc): Quantum circuit to print.
            name (str): Quantum circuit's name.
        """
        print(f"\n{name}:\n{circuit}")

    def _oracle(self, targets: set[str]) -> qc:
        return generic_oracle(targets)

    def _diffuser(self) -> qc:
        """Amplify target state(s) amplitude, which decreases the amplitudes of other states
        and increases the probability of getting the correct solution (i.e. target state(s)).

        Returns:
            qc: Quantum circuit representation of diffuser (i.e. Grover's diffusion operator).
        """
        # Create N-qubit quantum circuit for diffuser
        diffuser = qc(self._qubits, name = "Diffuser")

        # Hadamard gate
        diffuser.h(self._qubits)

        # Oracle with all zero target state
        diffuser.append(self._oracle({"0" * self.n_qubits}), list(range(self.n_qubits)))

        # Hadamard gate
        diffuser.h(self._qubits)
        
        # Display diffuser, if applicable
        if self.print_circuit: self._print_circuit(diffuser, "DIFFUSER")
        
        return diffuser

    def _grover(self) -> qc:
        """Create quantum circuit representation of Grover's algorithm,
        which consists of 4 parts: (1) state preparation/initialization,
        (2) oracle, (3) diffuser, and (4) measurement of resulting state.
        
        Steps 2-3 are repeated an optimal number of times (i.e. Grover's
        iterate) in order to maximize probability of success of Grover's algorithm.

        Returns:
            qc: Quantum circuit representation of Grover's algorithm.
        """
        # Create N-qubit quantum circuit for Grover's algorithm
        grover = qc(self._qubits, name = "Grover Circuit")
        
        # Intialize qubits with Hadamard gate (i.e. uniform superposition)
        grover.h(self._qubits)
        
        # # Apply barrier to separate steps
        grover.barrier()

        # Apply oracle and diffuser (i.e. Grover operator) optimal number of times
        for _ in range(int((pi / 4) * sqrt((2 ** self.n_qubits) / len(self._targets)))):
            grover.append(self._oracle(self._targets), list(range(self.n_qubits)))
            grover.append(self._diffuser(), list(range(self.n_qubits)))
        
        # Measure all qubits once finished
        grover.measure_all()

        # Display grover circuit, if applicable
        if self.print_circuit: self._print_circuit(grover, "GROVER CIRCUIT")
        
        return grover

    def _outcome(self, winners: list[str], counts: Counts) -> None:
        """Print top measurement(s) (state(s) with highest frequency)
        and target state(s) in binary and decimal form, determine
        if top measurement(s) equals target state(s), then print result.

        Args:
            winners (list[str]): State(s) (N-qubit binary string(s))
            with highest probability of being measured.
            counts (Counts): Each state and its respective frequency.
        """
        print("WINNER(S):")
        print(f"Binary = {winners}\nDecimal = {[ int(key, 2) for key in winners ]}\n")
            
        print("TARGET(S):")
        print(f"Binary = {self._targets}\nDecimal = {self.search}\n")

        if not all(key in self._targets for key in winners): print("Target(s) not found...")

        else:
            winners_frequency, total = 0, 0

            for value, frequency in counts.items():
                if value in winners:
                    winners_frequency += frequency
                total += frequency
            
            print(f"Target(s) found with {winners_frequency / total:.2%} accuracy!")

    def _show_histogram(self, histogram_data) -> None:
        """Print outcome and display histogram of simulation results.

        Args:
            data: Each state and its respective frequency.
        """
        # State(s) with highest count and their frequencies
        winners = { winner : histogram_data.get(winner) for winner in nlargest(len(self._targets), histogram_data, key = histogram_data.get) }

        # Print outcome
        self._outcome(list(winners.keys()), histogram_data)

        # X-axis and y-axis value(s) for winners, respectively
        winners_x_axis = [ str(winner) for winner in [*winners] ]
        winners_y_axis = [ *winners.values() ]

        # All other states (i.e. non-winners) and their frequencies
        others = { state : frequency for state, frequency in histogram_data.items() if state not in winners }

        # X-axis and y-axis value(s) for all other states, respectively
        other_states_x_axis = "Others" if self.combine_states else [*others]
        other_states_y_axis = [ sum([*others.values()]) ] if self.combine_states else [ *others.values() ]

        # Create histogram for simulation results
        figure, axes = subplots(num = "Grover's Algorithm — Results", layout = "constrained")
        axes.bar(winners_x_axis, winners_y_axis, color = "green", label = "Target")
        axes.bar(other_states_x_axis, other_states_y_axis, color = "red", label = "Non-target")
        axes.legend(fontsize = self.fontsize)
        axes.grid(axis = "y", ls = "dashed")
        axes.set_axisbelow(True)

        # Set histogram title, x-axis title, and y-axis title respectively
        axes.set_title(f"Outcome of {self.shots} Simulations", fontsize = int(self.fontsize * 1.45))
        axes.set_xlabel("States (Qubits)", fontsize = int(self.fontsize * 1.3))
        axes.set_ylabel("Frequency", fontsize = int(self.fontsize * 1.3))

        # Set font properties for x-axis and y-axis labels respectively
        xticks(fontsize = self.fontsize, family = "monospace", rotation = 0 if self.combine_states else 70)
        yticks(fontsize = self.fontsize, family = "monospace")
        
        # Set properties for annotations displaying frequency above each bar
        annotation = axes.annotate("",
                                xy = (0, 0),
                                xytext = (5, 5),
                                xycoords = "data",
                                textcoords = "offset pixels",
                                ha = "center",
                                va = "bottom",
                                family = "monospace",
                                weight = "bold",
                                fontsize = self.fontsize,
                                bbox = dict(facecolor = "white", alpha = 0.4, edgecolor = "None", pad = 0)
                                )
        
        def _hover(event) -> None:
            """Display frequency above each bar upon hovering over it.

            Args:
                event: Matplotlib event.
            """
            visibility = annotation.get_visible()
            if event.inaxes == axes:
                for bars in axes.containers:
                    for bar in bars:
                        cont, _ = bar.contains(event)
                        if cont:
                            x, y = bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height()
                            annotation.xy = (x, y)
                            annotation.set_text(y)
                            annotation.set_visible(True)
                            figure.canvas.draw_idle()
                            return
            if visibility:
                annotation.set_visible(False)
                figure.canvas.draw_idle()
            
        # Display histogram
        id = figure.canvas.mpl_connect("motion_notify_event", _hover)
        show()
        figure.canvas.mpl_disconnect(id)

    def run(self) -> None:
        """
        Run Grover's algorithm simulation.
        """
        # Simulate Grover's algorithm locally
        backend = AerSimulator(method = "density_matrix")

        # Generate optimized grover circuit for simulation
        transpiled_circuit = transpile(self._grover(), backend, optimization_level = 2)

        # Run Grover's algorithm simulation 
        job = backend.run(transpiled_circuit, shots = self.shots)

        # Get simulation results
        results = job.result()
        
        # Get each state's histogram data (including frequency) from simulation results
        data = results.get_counts()

        # Display simulation results
        self._show_histogram(data)

if __name__ == "__main__":
    GroversAlgorithm().run()