#!/usr/bin/env python
# coding: utf-8

# In[2]:
from dell_runtime import DellRuntimeProvider
from qiskit import QuantumCircuit
import pandas as pd
from time import sleep
import os


df = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + '/aux_file/dataset_graph7.csv',sep=',', header=None) # alterative problem: dataset_graph10.csv
data = df.values
provider = DellRuntimeProvider()


# In[26]:


print(df.head(4))


# In[31]:


RUNTIME_PROGRAM = """
# This code is part of qiskit-runtime.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=invalid-name

import itertools
import json
import numpy as np
from numpy.random import RandomState
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.compiler import transpile
from cvxopt import matrix, solvers  # pylint: disable=import-error


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


class KernelMatrix:
    def __init__(self, feature_map, backend, initial_layout=None):
        self._feature_map = feature_map
        self._feature_map_circuit = self._feature_map.construct_circuit
        self._backend = backend
        self._initial_layout = initial_layout

        self.results = {}

    def construct_kernel_matrix(self, x1_vec, x2_vec, parameters=None):
        is_identical = False
        if np.array_equal(x1_vec, x2_vec):
            is_identical = True

        experiments = []

        measurement_basis = "0" * self._feature_map._num_qubits

        if is_identical:

            my_product_list = list(
                itertools.combinations(range(len(x1_vec)), 2)
            )  # all pairwise combos of datapoint indices

            for index_1, index_2 in my_product_list:

                circuit_1 = self._feature_map_circuit(
                    x=x1_vec[index_1], parameters=parameters, name="{}_{}".format(index_1, index_2)
                )
                circuit_2 = self._feature_map_circuit(
                    x=x1_vec[index_2], parameters=parameters, inverse=True
                )
                circuit = circuit_1.compose(circuit_2)
                circuit.measure_all()
                experiments.append(circuit)

            experiments = transpile(
                experiments, backend=self._backend, initial_layout=self._initial_layout
            )
            program_data = self._backend.run(experiments, shots=8192).result()

            self.results["program_data"] = program_data

            mat = np.eye(
                len(x1_vec), len(x1_vec)
            )  # kernel matrix element on the diagonal is always 1
            for experiment, [index_1, index_2] in enumerate(my_product_list):

                counts = program_data.get_counts(experiment=experiment)
                shots = sum(counts.values())

                mat[index_1][index_2] = (
                    counts.get(measurement_basis, 0) / shots
                )  # kernel matrix element is the probability of measuring all 0s
                mat[index_2][index_1] = mat[index_1][index_2]  # kernel matrix is symmetric

            return mat

        else:

            for index_1, point_1 in enumerate(x1_vec):
                for index_2, point_2 in enumerate(x2_vec):

                    circuit_1 = self._feature_map_circuit(
                        x=point_1, parameters=parameters, name="{}_{}".format(index_1, index_2)
                    )
                    circuit_2 = self._feature_map_circuit(
                        x=point_2, parameters=parameters, inverse=True
                    )
                    circuit = circuit_1.compose(circuit_2)
                    circuit.measure_all()
                    experiments.append(circuit)

            experiments = transpile(
                experiments, backend=self._backend, initial_layout=self._initial_layout
            )
            program_data = self._backend.run(experiments, shots=8192).result()

            self.results["program_data"] = program_data

            mat = np.zeros((len(x1_vec), len(x2_vec)))
            i = 0
            for index_1, _ in enumerate(x1_vec):
                for index_2, _ in enumerate(x2_vec):

                    counts = program_data.get_counts(experiment=i)
                    shots = sum(counts.values())

                    mat[index_1][index_2] = counts.get(measurement_basis, 0) / shots
                    i += 1

            return mat


class QKA:
    def __init__(self, feature_map, backend, initial_layout=None, user_messenger=None):
        self.feature_map = feature_map
        self.feature_map_circuit = self.feature_map.construct_circuit
        self.backend = backend
        self.initial_layout = initial_layout
        self.num_parameters = self.feature_map._num_parameters

        self._user_messenger = user_messenger
        self.result = {}
        self.kernel_matrix = KernelMatrix(
            feature_map=self.feature_map, backend=self.backend, initial_layout=self.initial_layout
        )

    def spsa_parameters(self):
        spsa_params = np.zeros((5))
        spsa_params[0] = 0.05  # a
        spsa_params[1] = 0.1  # c
        spsa_params[2] = 0.602  # alpha
        spsa_params[3] = 0.101  # gamma
        spsa_params[4] = 0  # A

        return spsa_params

    def cvxopt_solver(self, K, y, C, max_iters=10000, show_progress=False):
        if y.ndim == 1:
            y = y[:, np.newaxis]
        H = np.outer(y, y) * K
        f = -np.ones(y.shape)

        n = K.shape[1]  # number of training points

        y = y.astype("float")

        P = matrix(H)
        q = matrix(f)
        G = matrix(np.vstack((-np.eye((n)), np.eye((n)))))
        h = matrix(np.vstack((np.zeros((n, 1)), np.ones((n, 1)) * C)))
        A = matrix(y, y.T.shape)
        b = matrix(np.zeros(1), (1, 1))

        solvers.options["maxiters"] = max_iters
        solvers.options["show_progress"] = show_progress

        ret = solvers.qp(P, q, G, h, A, b, kktsolver="ldl")

        return ret

    def spsa_step_one(self, lambdas, spsa_params, count):
        prng = RandomState(count)

        c_spsa = float(spsa_params[1]) / np.power(count + 1, spsa_params[3])
        delta = 2 * prng.randint(0, 2, size=np.shape(lambdas)[0]) - 1

        lambda_plus = lambdas + c_spsa * delta
        lambda_minus = lambdas - c_spsa * delta

        return lambda_plus, lambda_minus, delta

    def spsa_step_two(self, cost_plus, cost_minus, lambdas, spsa_params, delta, count):
        a_spsa = float(spsa_params[0]) / np.power(count + 1 + spsa_params[4], spsa_params[2])
        c_spsa = float(spsa_params[1]) / np.power(count + 1, spsa_params[3])

        g_spsa = (cost_plus - cost_minus) * delta / (2.0 * c_spsa)

        lambdas_new = lambdas - a_spsa * g_spsa
        lambdas_new = lambdas_new.flatten()

        cost_final = (cost_plus + cost_minus) / 2

        return cost_final, lambdas_new

    def align_kernel(self, data, labels, initial_kernel_parameters=None, maxiters=1, C=1):
        if initial_kernel_parameters is not None:
            lambdas = initial_kernel_parameters
        else:
            lambdas = np.random.uniform(-1.0, 1.0, size=(self.num_parameters))

        spsa_params = self.spsa_parameters()

        lambda_save = []
        cost_final_save = []

        for count in range(maxiters):

            lambda_plus, lambda_minus, delta = self.spsa_step_one(
                lambdas=lambdas, spsa_params=spsa_params, count=count
            )

            kernel_plus = self.kernel_matrix.construct_kernel_matrix(
                x1_vec=data, x2_vec=data, parameters=lambda_plus
            )
            kernel_minus = self.kernel_matrix.construct_kernel_matrix(
                x1_vec=data, x2_vec=data, parameters=lambda_minus
            )

            ret_plus = self.cvxopt_solver(K=kernel_plus, y=labels, C=C)
            cost_plus = -1 * ret_plus["primal objective"]

            ret_minus = self.cvxopt_solver(K=kernel_minus, y=labels, C=C)
            cost_minus = -1 * ret_minus["primal objective"]

            cost_final, lambda_best = self.spsa_step_two(
                cost_plus=cost_plus,
                cost_minus=cost_minus,
                lambdas=lambdas,
                spsa_params=spsa_params,
                delta=delta,
                count=count,
            )

            lambdas = lambda_best

            interim_result = {"cost": cost_final, "kernel_parameters": lambdas}
            print(interim_result)
            self._user_messenger.publish(interim_result)

            lambda_save.append(lambdas)
            cost_final_save.append(cost_final)

        # Evaluate aligned kernel matrix with optimized set of
        # parameters averaged over last 10% of SPSA steps:
        num_last_lambdas = int(len(lambda_save) * 0.10)
        if num_last_lambdas > 0:
            last_lambdas = np.array(lambda_save)[-num_last_lambdas:, :]
            lambdas = np.sum(last_lambdas, axis=0) / num_last_lambdas
        else:
            lambdas = np.array(lambda_save)[-1, :]

        kernel_best = self.kernel_matrix.construct_kernel_matrix(
            x1_vec=data, x2_vec=data, parameters=lambdas
        )

        self.result["aligned_kernel_parameters"] = lambdas
        self.result["aligned_kernel_matrix"] = kernel_best

        return self.result


def main(backend, user_messenger, **kwargs):
    # Reconstruct the feature map object.
    feature_map = kwargs.get("feature_map")
    fm = FeatureMap.from_json(feature_map)

    data = kwargs.get("data")
    labels = kwargs.get("labels")
    initial_kernel_parameters = kwargs.get("initial_kernel_parameters", None)
    maxiters = kwargs.get("maxiters", 1)
    C = kwargs.get("C", 1)
    initial_layout = kwargs.get("initial_layout", None)

    qka = QKA(
        feature_map=fm,
        backend=backend,
        initial_layout=initial_layout,
        user_messenger=user_messenger,
    )
    qka_results = qka.align_kernel(
        data=data,
        labels=labels,
        initial_kernel_parameters=initial_kernel_parameters,
        maxiters=maxiters,
        C=C,
    )

    user_messenger.publish(qka_results, final=True)
"""


# In[32]:


RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}


# In[33]:

# provider.remote(os.getenv("SERVER_URL"))
program_id = provider.runtime.upload_program(RUNTIME_PROGRAM, metadata=RUNTIME_PROGRAM_METADATA)


# In[34]:


import numpy as np
import featuremaps
# choose number of training and test samples per class:
num_train = 10
num_test = 10

# extract training and test sets and sort them by class label
train = data[:2*num_train, :]
test = data[2*num_train:2*(num_train+num_test), :]

ind=np.argsort(train[:,-1])
x_train = train[ind][:,:-1]
y_train = train[ind][:,-1]

ind=np.argsort(test[:,-1])
x_test = test[ind][:,:-1]
y_test = test[ind][:,-1]


C = 1
maxiters = 10
initial_point = [0.1]
initial_layout = [10, 11, 12, 13, 14, 15, 16]                   # see figure above for the 7-qubit graph
# initial_layout = [9, 8, 11, 14, 16, 19, 22, 25, 24, 23]       # see figure above for the 10-qubit graph

d = np.shape(data)[1]-1                                         # feature dimension is twice the qubit number

em = [[0,2],[3,4],[2,5],[1,4],[2,3],[4,6]]
fm = featuremaps.FeatureMap(feature_dimension=d, entangler_map=em)

program_inputs = {
    'feature_map': fm,
    'data': x_train,
    'labels': y_train,
    'initial_kernel_parameters': initial_point,
    'maxiters': maxiters,
    'C': C,
    'initial_layout': initial_layout
}

runtime_program = provider.runtime.program(program_id)
job = provider.runtime.run(program_id, options=None, inputs=program_inputs)

res = job.result(timeout=600)
print(res)
