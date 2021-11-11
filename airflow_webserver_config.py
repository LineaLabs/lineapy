# turn off auth https://airflow.apache.org/docs/apache-airflow/stable/security/webserver.html#web-authentication
AUTH_ROLE_PUBLIC = "Admin"
# Turn off CSRF so we can submit froms from another URL on codespaces
WTF_CSRF_ENABLED = False
