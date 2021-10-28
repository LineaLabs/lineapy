import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

from pandas.api.types import CategoricalDtype
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

from sklearn.feature_extraction import DictVectorizer
from sklearn import linear_model as lm


default_dag_args = {
    "owner": "airflow",
    "retries": 2,
    "start_date": days_ago(1),
}

"""
I need to process all the code from the notebooks
"""

    

def evalute_perf(model, val):
    X_val = val.drop(['SalePrice'], axis = 1)
    y_val = val.loc[:, 'SalePrice']
    y_predicted = linear_model.predict(X_val)
    return y_predicted, y_val
    
def process_1(state, ti):
    assets = pd.read_csv("../ames_train_cleaned.csv")

    cleaned_data = training_data.drop(['Pool_QC', 'Misc_Feature'], axis=1)
    cleaned_data = cleaned_data[cleaned_data['Garage_Area']  < 1250]
    vec_enc = DictVectorizer()
    vec_enc.fit(cleaned_data[['Neighborhood']].to_dict(orient='records'))
    Neighborhood_data = vec_enc.transform(cleaned_data[['Neighborhood']].to_dict(orient='records')).toarray()
    Neighborhood_cats = vec_enc.get_feature_names()
    Neighborhood = pd.DataFrame(Neighborhood_data, columns=Neighborhood_cats)
    cleaned_data = pd.concat([cleaned_data, Neighborhood], axis=1)
    cleaned_data = cleaned_data.drop(columns=Neighborhood_cats[0])
    cleaned_data = cleaned_data.dropna()
    train, val = train_test_split(cleaned_data, test_size=0.3, random_state=42)
    X_train = train.drop(['SalePrice'], axis = 1)
    y_train = train.loc[:, 'SalePrice']
    linear_model = lm.LinearRegression(fit_intercept=True)
    model.fit(X_train, y_train)
    X_val = val.drop(['SalePrice'], axis = 1)
    y_val = val.loc[:, 'SalePrice']
    y_predicted = linear_model.predict(X_val)
    
    rmse_val = np.sqrt(np.mean((y_predicted, y_val)**2))
    logging.info('Performance for process 1:', rmse_val)
    
    
def process_2(state, ti):
    assets = pd.read_csv("../ames_train_cleaned.csv")

    from pandas.api.types import CategoricalDtype
    from sklearn.feature_extraction import DictVectorizer
    cleaned_data = training_data.drop(['Pool_QC', 'Misc_Feature'], axis=1)
    cleaned_data = cleaned_data[cleaned_data['Garage_Area']  < 1250]
    vec_enc = DictVectorizer()
    vec_enc.fit(cleaned_data[['Neighborhood']].to_dict(orient='records'))
    Neighborhood_data = vec_enc.transform(cleaned_data[['Neighborhood']].to_dict(orient='records')).toarray()
    Neighborhood_cats = vec_enc.get_feature_names()
    Neighborhood = pd.DataFrame(Neighborhood_data, columns=Neighborhood_cats)
    cleaned_data = pd.concat([cleaned_data, Neighborhood], axis=1)
    cleaned_data = cleaned_data.drop(columns=Neighborhood_cats[0])
    ti.xcom_push(key='cleaned_data', value=cleaned_data)
    cleaned_data = cleaned_data.dropna()
    cleaned_data['SalePrice'] = np.log(cleaned_data['SalePrice'])
    from sklearn.model_selection import train_test_split
    train, val = train_test_split(cleaned_data, test_size=0.3, random_state=42)
    from sklearn.feature_extraction import DictVectorizer
    from sklearn import linear_model as lm
    X_train = train.drop(['SalePrice'], axis = 1)
    y_train = train.loc[:, 'SalePrice']
    linear_model = lm.LinearRegression(fit_intercept=True)
    linear_model.fit(X_train, y_train)
    
    X_val = val.drop(['SalePrice'], axis = 1)
    y_val = val.loc[:, 'SalePrice']
    y_predicted = linear_model.predict(X_val)
    rmse_val = np.sqrt(np.mean((np.exp(y_predicted), np.exp(y_val))**2)
    logging.info('Performance for process 2:', rmse_val)
    
    
dag = DAG(
    dag_id="housing prediction initial models",
    schedule_interval="*/* * * * *", # I will figure out how to re-run later
    max_active_runs=1,
    catchup=False,
    default_args=default_dag_args,
)
                       

model_dag = PythonOperator(
    dag=dag,
    task_id=f"process_1_dag",
    python_callable=process_1,
)
                       
alt_model_dag = PythonOperator(
    dag=dag,
    task_id=f"process_2_dag",
    python_callable=process_2,
)
