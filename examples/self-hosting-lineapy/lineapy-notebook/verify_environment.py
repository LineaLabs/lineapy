import lineapy

assert(lineapy.options.get('database_url') == 'postgresql://lineapy:lineapypassword@postgres-lineapy:5432/lineapy_artifact_store')
assert(lineapy.options.get('artifact_storage_dir') == 's3://lineapy-artifact-store')
assert(lineapy.options.get('storage_options') is not None)

print("Lineapy configuration verified.")