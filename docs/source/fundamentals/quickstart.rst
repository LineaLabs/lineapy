.. _quickstart:

Quick Start
===========

.. note::
    Make sure that you have LineaPy installed. You can find relevant instructions 
    in the :ref:`Installation <setup>` section.

Let’s start with a simple example that demonstrates how to use LineaPy to store and
analyze a variable's history.

In an interactive computing environment such as Jupyter Notebook, we often find our work
evolving incrementally. That is, our code takes different turns to reflect our thought stream.
The following exemplifies this type of “dynamism” in interactive computing:

.. code:: python

    import lineapy

    # Define text to display in page heading
    text = "Greetings"

    # Change heading text
    text = "Hello"

    # Augment heading text
    text = text + " World!"

    # Try an alternative display
    alt_text = text.split()

Now, let’s say we have reached the end of our programming session and decided that we like
what we see when we ``print(text)``. As shown above, ``text`` has gone through different
modifications, and it might not be clear how it reached its final state especially given other
extraneous operations between these modifications. We can cut through this by running:

.. code:: python

    # Store the variable’s history or “lineage”
    lineapy.save(text, "text_for_heading")

    # Retrieve the stored “artifact”
    artifact = lineapy.get("text_for_heading")

    # Obtain the simplest version of a variable's history
    print(artifact.code)

which will show:

.. code:: python

    text = "Hello"
    text = text + " World!"

Note that these are the minimal essential steps to get to the final state of the variable ``text``.

.. note::
    In fact, ``lineapy.save()`` itself returns the artifact object, so we could have simply
    executed ``artifact = lineapy.save(text, "text_for_heading")`` above.

For more detailed examples, check out our `tutorial notebooks <https://github.com/LineaLabs/lineapy/tree/main/examples>`_.
