import pandas as pd
from sklearn.ensemble import RandomForestClassifier
assets = pd.read_csv("ames_train_cleaned.csv")
def is_new(col):
    return col > 1970
assets["is_new"] = is_new(assets["Year_Built"])
clf = RandomForestClassifier(random_state=0)
y = assets["is_new"]
x = assets[["SalePrice", "Lot_Area", "Garage_Area"]]
clf.fit(x, y)
p = clf.predict([[100 * 1000, 10, 4]])
