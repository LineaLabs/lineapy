# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/xgboost/demo/guide-python/basic_walkthrough.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[xgboost_basic_walkthrough]'

"""
Getting started with XGBoost
============================
"""
import numpy as np
import scipy.sparse
import pickle
import xgboost as xgb
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
XGBOOST_ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DEMO_DIR = os.path.join(XGBOOST_ROOT_DIR, "demo")
dtrain = xgb.DMatrix(
    os.path.join(DEMO_DIR, "data", "agaricus.txt.train?indexing_mode=1")
)
dtest = xgb.DMatrix(os.path.join(DEMO_DIR, "data", "agaricus.txt.test?indexing_mode=1"))
param = {"max_depth": 2, "eta": 1, "objective": "binary:logistic"}
watchlist = [(dtest, "eval"), (dtrain, "train")]
num_round = 2
bst = xgb.train(param, dtrain, num_round, watchlist)
preds = bst.predict(dtest)
labels = dtest.get_label()
print(
    "error=%f"
    % (
        sum(1 for i in range(len(preds)) if int(preds[i] > 0.5) != labels[i])
        / float(len(preds))
    )
)
bst.save_model("0001.model")
bst.dump_model("dump.raw.txt")
bst.dump_model("dump.nice.txt", os.path.join(DEMO_DIR, "data/featmap.txt"))
dtest.save_binary("dtest.buffer")
bst.save_model("xgb.model")
bst2 = xgb.Booster(model_file="xgb.model")
dtest2 = xgb.DMatrix("dtest.buffer")
preds2 = bst2.predict(dtest2)
assert np.sum(np.abs(preds2 - preds)) == 0
pks = pickle.dumps(bst2)
bst3 = pickle.loads(pks)
preds3 = bst3.predict(dtest2)
assert np.sum(np.abs(preds3 - preds)) == 0
print("start running example of build DMatrix from scipy.sparse CSR Matrix")
labels = []
row = []
col = []
dat = []
i = 0
for l in open(os.path.join(DEMO_DIR, "data", "agaricus.txt.train")):
    arr = l.split()
    labels.append(int(arr[0]))
    for it in arr[1:]:
        k, v = it.split(":")
        row.append(i)
        col.append(int(k))
        dat.append(float(v))
    i += 1
csr = scipy.sparse.csr_matrix((dat, (row, col)))
dtrain = xgb.DMatrix(csr, label=labels)
watchlist = [(dtest, "eval"), (dtrain, "train")]
bst = xgb.train(param, dtrain, num_round, watchlist)
print("start running example of build DMatrix from scipy.sparse CSC Matrix")
csc = scipy.sparse.csc_matrix((dat, (row, col)))
dtrain = xgb.DMatrix(csc, label=labels)
watchlist = [(dtest, "eval"), (dtrain, "train")]
bst = xgb.train(param, dtrain, num_round, watchlist)
print("start running example of build DMatrix from numpy array")
npymat = csr.todense()
dtrain = xgb.DMatrix(npymat, label=labels)
watchlist = [(dtest, "eval"), (dtrain, "train")]
bst = xgb.train(param, dtrain, num_round, watchlist)
