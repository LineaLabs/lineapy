import altair as alt
from pandas import read_csv
from seaborn import relplot
from sklearn.ensemble import RandomForestClassifier

assets = read_csv("ames_train_cleaned.csv")

assets["is_new"] = assets["Year_Built"]

clf = RandomForestClassifier(random_state=0)
y = assets["is_new"]
x = assets[["SalePrice"]]

clf.fit(x, y)
p = clf.predict([[1000]])
print("p value", p)
