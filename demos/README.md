# LineaPy Use Cases

## `predict_house_price`

This use case illustrates how LineaPy can facilitate an end-to-end data science workflow for housing price prediction.
The notebook comes in 3 main sections:

1. ***Exploratory Data Analysis and Feature Engineering.*** Using various statistics and visualizations, we explore the given data
to create useful features. We use LineaPy to store the transformed data as an artifact, which allows us to automatically refactor and clean up the code.

2. ***Training a Model.*** Using the transformed data, we train a model that can predict housing prices. We then store
the trained model as an artifact.

3. ***Building an End-to-End Pipeline.*** Using artifacts saved in this session, we quickly build an end-to-end
pipeline that combines data preprocessing and model training, moving closer to production.
