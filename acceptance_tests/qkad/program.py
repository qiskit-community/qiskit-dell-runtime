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
from qtils.featuremap import FeatureMap
from qtils.qka import QKA
import os
import pandas as pd


def main(backend, user_messenger, **kwargs):

    df = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + '/aux_file/dataset_graph7.csv',sep=',', header=None) # alterative problem: dataset_graph10.csv
    data = df.values

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
    maxiters = 1
    initial_point = [0.1]
    initial_layout = [10, 11, 12, 13, 14, 15, 16]                   # see figure above for the 7-qubit graph
    # initial_layout = [9, 8, 11, 14, 16, 19, 22, 25, 24, 23]       # see figure above for the 10-qubit graph

    d = np.shape(data)[1]-1                                         # feature dimension is twice the qubit number

    em = [[0,2],[3,4],[2,5],[1,4],[2,3],[4,6]]
    fm = FeatureMap(feature_dimension=d, entangler_map=em)

    qka = QKA(
        feature_map=fm,
        backend=backend,
        initial_layout=initial_layout,
        user_messenger=user_messenger,
    )
    qka_results = qka.align_kernel(
        data=x_train,
        labels=y_train,
        initial_kernel_parameters=initial_point,
        maxiters=maxiters,
        C=C,
    )

    user_messenger.publish(qka_results, final=True)