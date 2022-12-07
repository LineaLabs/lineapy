.. _annotate_package:

Annotate Packages
=================

.. include:: ../../../snippets/slack_support.rstinc

One big strength of the Python language is its large and active development community. This means that
we have a lot of interesting and useful Python packages that are not part of the core Python distribution.
These third-party packages often come with their own new APIs, and LineaPy is not guaranteed to handle all
of them properly when :ref:`removing extraneous code <code_cleanup>`. For such "unrecognized" APIs, we can add
instructions for LineaPy, which we call "package annotation". Specifically, package annotation is done by creating
or updating a YAML file in `lineapy/annotations/external/ <https://github.com/LineaLabs/lineapy/tree/main/lineapy/annotations/external>`_
(check the link for existing annotations).

.. warning::

    Note that YAML files are sensitive to indentation. To ensure that you use correct indentation, we recommend you
    consult/adapt `existing annotation files <https://github.com/LineaLabs/lineapy/tree/main/lineapy/annotations/external>`_.

Annotating APIs that modify external states
-------------------------------------------

A common group of APIs that LineaPy needs annotation for are those that modify external states
such as the local file system and external databases.

For instance, without relevant package annotation, running

.. code-block:: python

    import pandas as pd
    import lineapy

    df = pd.read_csv("https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv")
    df["variety_color"] = df["variety"].map({"Setosa": 0, "Versicolor": 1, "Virginica": 2})
    df.to_csv("df_augmented.csv", index=False)
    artifact = lineapy.save(lineapy.file_system, "df_augmented")

    print(artifact.get_code())

would display nothing. This is because ``lineapy`` does not recognize
`to_csv <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html>`_
as an API that modifies external states (local file system, in this case) and hence skips it
during the relevant code cleanup.

In contrast, we would get the correct code cleanup with the following package annotation (currently in the source code):

.. code-block:: yaml

    # pandas.annotations.yaml

    - module: pandas.core.generic
      annotations:
        - criteria:
            class_instance: NDFrame
            class_method_names:
              - to_csv
          side_effects:
            - mutated_value:
                external_state: file_system

where

* ``module`` refers to the third-party package/module that the annotation is associated with.

* ``criteria`` specifies what each annotation is *for*. In this example, it instructs that the annotation is for ``to_csv`` method of ``NDFrame`` class.

* ``side_effects`` specifies what each annotation is *about*. In this example, it instructs that the annotation is about mutation of an external state, specifically the local file system.

In sum, these instructions tell ``lineapy`` to recognize ``to_csv`` method of ``NDFrame`` class (defined under ``pandas.core.generic`` module)
as an API that mutates the local file system, and to treat it as such in relevant downstream tasks such as code cleanup.

.. note::

    ``NDFrame`` is a parent class of ``DataFrame``, where the latter inherits ``to_csv`` method from the former.
    Hence, the annotation above is done at a more fundamental level, which is recommended to avoid redundant annotations
    among related classes (i.e., other data classes that inherit from ``NDFrame``). In practice, identifying the right
    "root" level to annotate at often involves exploring the target package's codebase for some time.

.. note::

    Hyphen at the beginning of each keyword indicates that the indented block is an item of a list. For instance, in the example above,
    ``- criteria`` means that the indented block following it, i.e.,

    .. code-block:: yaml

        criteria:
          class_instance: NDFrame
          class_method_names:
            - to_csv
        side_effects:
          - mutated_value:
              external_state: file_system

    is an item of ``annotations`` list. Hence, we can add another annotation for ``to_json`` like so:

    .. code-block:: yaml
        :emphasize-lines: 12, 13, 14, 15, 16, 17, 18

        # pandas.annotations.yaml

        - module: pandas.core.generic
          annotations:
            - criteria:
                class_instance: NDFrame
                class_method_names:
                  - to_csv
              side_effects:
                - mutated_value:
                    external_state: file_system
            - criteria:
                class_instance: NDFrame
                class_method_names:
                  - to_json
              side_effects:
                - mutated_value:
                    external_state: file_system

    In fact, since the two items share much in common (the only difference is in ``class_method_names``),
    we can condense the above annotation to the following:

    .. code-block:: yaml
        :emphasize-lines: 9

        # pandas.annotations.yaml

        - module: pandas.core.generic
          annotations:
            - criteria:
                class_instance: NDFrame
                class_method_names:
                  - to_csv
                  - to_json
              side_effects:
                - mutated_value:
                    external_state: file_system

    where we simply extend ``class_method_names`` list instead.

Annotating APIs that modify the caller itself
---------------------------------------------

Another group of APIs that need annotation are those that modify their caller.

For instance, without relevant package annotation, running

.. code-block:: python

    from sklearn.linear_model import LinearRegression
    import pandas as pd
    import lineapy

    df = pd.read_csv("https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv")
    mod = LinearRegression()
    mod.fit(X=df[["petal.width"]], y=df["sepal.width"])
    artifact = lineapy.save(mod, "fitted_model")

    print(artifact.get_code())

would display

.. code-block:: none

    from sklearn.linear_model import LinearRegression

    mod = LinearRegression()

where the critical step of model fitting is missing. This is because ``lineapy`` does not recognize
`fit <https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html#sklearn.linear_model.LinearRegression.fit>`_
as an API that modifies the caller (``mod`` of ``LinearRegression`` type, in this case) and hence skips it
during the relevant code cleanup.

In contrast, we would get the correct code cleanup with the following package annotation (currently in the source code):

.. code-block:: yaml

    # sklearn.annotations.yaml

    - module: sklearn.base
      annotations:
        - criteria:
            class_instance: BaseEstimator
            class_method_name: fit
          side_effects:
            - mutated_value:
                self_ref: SELF_REF
            - views:
                - self_ref: SELF_REF
                - result: RESULT

where

* ``BaseEstimator`` is a parent class of ``LinearModel``, which is in turn a parent class of ``LinearRegression``.

* ``views`` specifies entities whose modifications should be linked to one another. In this example, ``result`` and ``self_ref`` are set to be views of each other, which means that modification of the ``fit`` call's output (e.g., ``fitted_mod`` in ``fitted_mod = mod.fit(...)``) will modify the ``fit`` caller itself (e.g., ``mod`` in ``fitted_mod = mod.fit(...)``), and vice versa. Differently put, ``views`` establishes links between objects that need to be tracked together because a change in one will change the other(s).

In sum, instructions above tell ``lineapy`` to recognize ``fit`` method of ``BaseEstimator`` class (defined under ``sklearn.base`` module)
as an API that mutates the function caller itself, and to treat it as such in relevant downstream tasks such as code cleanup.
