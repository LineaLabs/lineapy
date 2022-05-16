import pickle


def a():
    a = [1, 2, 3]
    res = pickle.dump(a, open("/tmp/fake", "wb"))
