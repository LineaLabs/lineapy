.. _quickstart:

Quick Start
===========

.. note::
    Make sure that you have LineaPy installed. You can find relevant instructions 
    in the :ref:`Installation <setup>` section.

Once you have LineaPy installed, you are ready to start using the package. We can start with a simple
example that demonstrates how to use LineaPy to store a variable's history. The ``lineapy.save()`` function
removes extraneous code to give you the simplest version of a variable's history.

Say we have development code looking as follows:

.. code:: python

    import lineapy

    # Define text to display in page heading
    text = "Greetings"

    # Some irrelevant operation
    num = 1 + 2

    # Change heading text
    text = "Hello"

    # Another irrelevant operation
    num_squared = num**2

    # Augment heading text
    text = text + " World!"

    # Try an alternative display
    alt_text = text.split()

Now, we have reached the end of our development session and decided that we like
what we see when we ``print(text)``. As shown above, ``text`` has gone through different
modifications, and it might not be clear how it reached its final state especially given other
extraneous operations between these modifications. We can cut through this by running:

.. code:: python

    # Store the variable’s history or “lineage”
    lineapy.save(text, "text_for_heading")

    # Retrieve the stored “artifact”
    artifact = lineapy.get("text_for_heading")

    # Obtain the simplest version of a variable's history
    print(artifact.get_code())

which will print:

.. code:: none

    text = "Hello"
    text = text + " World!"

Note that these are the minimal essential steps to get to the final state of the variable ``text``.
That is, LineaPy has performed code cleanup on our behalf, moving us a step closer to production.

.. note::
    In fact, ``lineapy.save()`` itself returns the artifact object, so we could have simply
    executed ``artifact = lineapy.save(text, "text_for_heading")`` above.

For more detailed examples, check out our `tutorial notebooks <https://github.com/LineaLabs/lineapy/tree/main/examples/tutorials>`_.
