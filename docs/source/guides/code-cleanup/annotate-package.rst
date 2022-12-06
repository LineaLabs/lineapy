Annotating Third-Party APIs
===========================

.. include:: ../../../snippets/slack_support.rstinc

Python ecosystem offers a lot of interesting and useful packages that are not part of the core distribution.
These third-party packages often come with their own new APIs, and LineaPy is not guaranteed to handle all
of them properly when :ref:`removing extraneous code <code_cleanup>`. For such "unrecognized" APIs, we can add
instructions for LineaPy, which we call "package annotation".

For instance, without relevant package annotation, running

.. code-block:: python

   import pyperclip

   pyperclip.copy("This wont show up without annotations")
   tmp_var = pyperclip.paste()
   artifact = lineapy.save(tmp_var, "annotated_text")

   print(artifact.get_code())

would display

.. code-block:: none

   import pyperclip

   tmp_var = pyperclip.paste()

where the ``pyperclip.copy`` step is missing. This is because ``lineapy`` does not recognize it
as an API that modifies the caller (``pyperclip``, in this case) and hence skips it
during the relevant code cleanup.

We can annotate the ``pyperclip`` package by creating a YAML file looking as follows:

.. code-block:: yaml

   # ./pyperclip.annotations.yaml

   - module: pyperclip
     annotations:
       - criteria:
           function_names:
             - copy
             - paste
         side_effects:
           - mutated_value:
               self_ref: SELF_REF

where

* ``module`` refers to the third-party package/module that the annotation is associated with.

* ``criteria`` specifies what each annotation is *for*. In this example, it instructs that the annotation is for ``copy`` and ``paste`` functions in the module.

* ``side_effects`` specifies what each annotation is *about*. In this example, it instructs that the annotation is about mutation of the function caller.

In sum, these instructions tell ``lineapy`` to recognize ``copy`` and ``paste`` functions in the ``pyperclip`` module
as APIs that mutate their caller, and to treat them as such in relevant downstream tasks such as code cleanup.

.. note::

   For more details on annotation keywords, check this :ref:`page <annotate_package>`.

To make the annotation take effect, we run:

.. code-block:: bash

   lineapy annotate add "./pyperclip.annotations.yaml" --name="pyperclip_annotations" 

where ``"pyperclip_annotations"`` is a name of our choice.

Now, if we reload ``lineapy`` and run the original code above, we get the correct code cleanup displayed:

.. code-block:: none

   import pyperclip

   pyperclip.copy("This wont show up without annotations")
   tmp_var = pyperclip.paste()

.. warning::

   Annotations added this way are valid in the local environment only.
   To integrate new annotations into the ``lineapy`` source code, the YAML file
   should be created or updated in `lineapy/annotations/external/ <https://github.com/LineaLabs/lineapy/tree/main/lineapy/annotations/external>`_,
   following contribution instructions :ref:`here <contribution_setup_and_basics>`.

To view imported annotations, run:

.. code-block:: bash

   lineapy annotate list

To delete imported annotations, run:

.. code-block:: bash

   lineapy annotate delete --name=[NAME-OF-ANNOTATION]

where ``[NAME-OF-ANNOTATION]`` is ``"pyperclip_annotations"`` in this example.
