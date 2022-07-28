import lineapy

art = {}
import pandas as pd
from sklearn.linear_model import LinearRegression

# Load train data
url1 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
train_df = pd.read_csv(url1)
# Initiate the model
mod = LinearRegression()
# Fit the model
mod.fit(
    X=train_df[["petal.width"]],
    y=train_df["petal.length"],
)
# Save the fitted model as an artifact
art["model"] = lineapy.save(mod, "iris_model")
# Load data to predict (assume it comes from a different source)
pred_df = pd.read_csv(url1)
# Make predictions
petal_length_pred = mod.predict(X=pred_df[["petal.width"]])
# Save the predictions
art["pred"] = lineapy.save(petal_length_pred, "iris_petal_length_pred")
