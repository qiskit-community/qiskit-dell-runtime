import itertools
import json
import numpy as np
from numpy.random import RandomState
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.compiler import transpile
from cvxopt import matrix, solvers  # pylint: disable=import-error

