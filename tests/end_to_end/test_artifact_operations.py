from lineapy.instrumentation.tracer_context import TracerContext


def test_slice_preserved_after_tracer_dereferenced(execute):
    importl = """import lineapy
"""
    artifact_f_save = """
lineapy.save(y, "deferencedy")
use_y = lineapy.get("deferencedy")
"""
    # choosing a mutating list here so that we can also verify that the
    # mutated node ids that get updated are correctly referenced
    # without the tracer dicts to point us to the right/mutated node id.
    code_body = """y = []
x = [y]
y.append(10)
x[0].append(11)
"""
    first_tracer = execute(
        importl + code_body + artifact_f_save, snapshot=False
    )
    # get the artifact from the first execution. we will use just this to recreate
    # the code slice/graph/airflow pipeline etc.
    # In this test we'll only test to see if code slice matches assuming
    # the rest will make sense if we have code slice.
    artifact_f = first_tracer.values["use_y"]
    # this simulates the first "session" is over and the user is starting over with just the db.
    del first_tracer
    # simulating the user using the db url/instance to recreate the db. and choosing the
    # last session or a particular session in case of a versioned artifact to recreate the graph for it.
    second_context = TracerContext.reload_session(
        artifact_f.db, artifact_f._session_id
    )
    # this is an additional redundant step to make sure our orig artifact is correct
    assert artifact_f.get_code() == code_body
    # and here we only use the tracer context to ensure we can retrieve the
    # slice from db directly
    assert second_context.slice("deferencedy") == code_body
