# Import libraries
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

import lineapy

# In[63]:


# Load dataset
df = pd.read_csv("./data/mushroom.csv")


# In[64]:


# Declare feature vector and target variable
X = df.drop(["class"], axis=1)
y = df["class"]


# In[65]:


# Encode categorical variables
X = pd.get_dummies(X, prefix_sep="_")
y = LabelEncoder().fit_transform(y)


# In[66]:


# Normalize feature vector
X2 = StandardScaler().fit_transform(X)


# In[67]:


# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X2, y, test_size=0.30, random_state=0
)


# In[68]:


# instantiate the classifier with n_estimators = 100
clf = RandomForestClassifier(n_estimators=100, random_state=0)


# In[69]:


# fit the classifier to the training set
clf.fit(X_train, y_train)


# In[70]:


# predict on the test set
y_pred = clf.predict(X_test)


# ## **Feature Importance**
#
# - Decision Trees models which are based on ensembles (eg. Extra Trees and Random Forest) can be used to rank the importance of the different features. Knowing which features our model is giving most importance can be of vital importance to understand how our model is making it’s predictions (therefore making it more explainable). At the same time, we can get rid of the features which do not bring any benefit to our model.

# In[71]:


# visualize feature importance

plt.figure(num=None, figsize=(10, 8), dpi=80, facecolor="w", edgecolor="k")

feat_importances = pd.Series(clf.feature_importances_, index=X.columns)

feat_importances.nlargest(7).plot(kind="barh")
lineapy.save(feat_importances, "mushroom feature importance")
