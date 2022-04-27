import pandas as pd

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
iris = pd.read_csv(url)
iris.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
del iris["class"]
iris = iris.dropna(how="any")
iris = iris.reset_index(drop=True)
linea_artifact_value = iris
