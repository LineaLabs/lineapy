import pytest

from lineapy.utils.utils import prettify

cv2 = pytest.importorskip("cv2")


@pytest.mark.slow
def test_opencv_knn(execute):
    code = """import cv2 as cv
import numpy as np
numpy.random.seed(0)
trainData = np.random.randint(0,100,(25,2)).astype(np.float32)
responses = np.random.randint(0,2,(25,1)).astype(np.float32)
red = trainData[responses.ravel()==0]
blue = trainData[responses.ravel()==1]
newcomer = np.random.randint(0,100,(1,2)).astype(np.float32)
knn = cv.ml.KNearest_create()
knn.train(trainData, cv.ml.ROW_SAMPLE, responses)
ret, results, neighbours ,dist = knn.findNearest(newcomer, 3)
"""
    res = execute(code, artifacts=["results", "neighbours", "dist"])
    assert res.values["results"].tolist() == [[0]]
    assert res.values["neighbours"].tolist() == [[1.0, 0, 0]]
    assert res.values["dist"].tolist() == [[85.0, 109.0, 353.0]]


@pytest.mark.slow
def test_opencv_lr(execute):
    code = """import cv2 as cv
import numpy as np
numpy.random.seed(0)
trainData = np.random.randint(0,100,(25,2)).astype(np.float32)
responses = np.random.randint(0,2,(25,1)).astype(np.float32)
red = trainData[responses.ravel()==0]
blue = trainData[responses.ravel()==1]
newcomer = np.random.randint(0,100,(1,2)).astype(np.float32)
lr = cv.ml.LogisticRegression_create()
lr.setTrainMethod(cv.ml.LogisticRegression_MINI_BATCH)
lr.setMiniBatchSize(1)
lr.setIterations(100)
lr.train(trainData, cv.ml.ROW_SAMPLE, responses)
ret, results = lr.predict(newcomer)
"""
    res = execute(code, artifacts=["results"])
    assert res.values["results"].tolist() == [[1.0]]
