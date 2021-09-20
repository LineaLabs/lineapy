import altair as alt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

alt.data_transformers.enable('json')
alt.renderers.enable('mimetype')

assets = pd.read_csv("ames_train_cleaned.csv")

sns.relplot(data=assets,
            x="Year_Built", y="SalePrice", size='Lot_Area')


def get_threshold():
    return 1970


def is_new(col):
    return col > get_threshold()


assets['is_new'] = is_new(assets['Year_Built'])

clf = RandomForestClassifier(random_state=0)
y = assets['is_new']
x = assets[['SalePrice', 'Lot_Area', 'Garage_Area']]

clf.fit(x, y)
p = clf.predict([[100 * 1000, 10, 4]])
print("p value", p)
