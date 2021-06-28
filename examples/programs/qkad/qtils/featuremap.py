import itertools
import json
import numpy as np
from numpy.random import RandomState
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.compiler import transpile
from cvxopt import matrix, solvers  # pylint: disable=import-error
from .qka import QKA

class FeatureMap:

    def __init__(self, feature_dimension, entangler_map=None):
        if isinstance(feature_dimension, int):
            if feature_dimension % 2 == 0:
                self._feature_dimension = feature_dimension
            else:
                raise ValueError("Feature dimension must be an even integer.")
        else:
            raise ValueError("Feature dimension must be an even integer.")

        self._num_qubits = int(feature_dimension / 2)

        if entangler_map is None:
            self._entangler_map = [
                [i, j]
                for i in range(self._feature_dimension)
                for j in range(i + 1, self._feature_dimension)
            ]
        else:
            self._entangler_map = entangler_map

        self._num_parameters = self._num_qubits

    def construct_circuit(self, x=None, parameters=None, q=None, inverse=False, name=None):

        if parameters is not None:
            if isinstance(parameters, (int, float)):
                raise ValueError("Parameters must be a list.")
            if len(parameters) == 1:
                parameters = parameters * np.ones(self._num_qubits)
            else:
                if len(parameters) != self._num_parameters:
                    raise ValueError(
                        "The number of feature map parameters must be {}.".format(
                            self._num_parameters
                        )
                    )

        if len(x) != self._feature_dimension:
            raise ValueError(
                "The input vector must be of length {}.".format(self._feature_dimension)
            )

        if q is None:
            q = QuantumRegister(self._num_qubits, name="q")

        circuit = QuantumCircuit(q, name=name)

        for i in range(self._num_qubits):
            circuit.ry(-parameters[i], q[i])

        for source, target in self._entangler_map:
            circuit.cz(q[source], q[target])

        for i in range(self._num_qubits):
            circuit.rz(-2 * x[2 * i + 1], q[i])
            circuit.rx(-2 * x[2 * i], q[i])

        if inverse:
            return circuit.inverse()
        else:
            return circuit

    def to_json(self):
        return json.dumps(
            {"feature_dimension": self._feature_dimension, "entangler_map": self._entangler_map}
        )

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

