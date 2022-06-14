import pickle


def a():

    a = [1, 2, 3]
    res = pickle.dump(a, open("pickle-sample.pkl", "wb"))
