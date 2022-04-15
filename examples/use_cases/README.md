# LineaPy Use Cases

## `predict_house_price`

This use case illustrates how LineaPy can facilitate an end-to-end data science workflow for housing price prediction.
It consists of three notebooks that each represent a phase/step in data science workflow:

1. ***Data Exploration and Preprocessing.*** Using various statistics and visualizations, we explore the given data
to create useful features. We use LineaPy to store the transformed data as an artifact, which allows us to automatically
a) refactor the code and b) build a pipeline for data preprocessing.

2. ***Training a Model.*** Using the transformed data, we train a model that can predict housing prices. We then store
the trained model as an artifact, which automatically refactors the development code.

3. ***Building an End-to-End Pipeline.*** Using artifacts stored in previous sessions, we quickly build an end-to-end
pipeline that combines data preprocessing and model training, moving closer to production.
