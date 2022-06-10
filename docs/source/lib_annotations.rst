.. _lib_annotations:

This document describes how to add new library annotations.

What library annotations are
----------------------------

Linea requires library functions to be annotated of their "side effects", such 
as whether a class method mutates the original object.



Linea uses these annotations for both `internal <https://github.com/LineaLabs/lineapy/blob/main/lineapy/annotations/internal>`__ 
libraries, such as ``os`` and ``operator``, and `external <https://github.com/LineaLabs/lineapy/blob/main/lineapy/annotations/external>`__
libraries, such as ``pandas`` and ``boto3``.

What we currently support
-------------------------
We are in the process of augmenting `external <https://github.com/LineaLabs/lineapy/blob/main/lineapy/annotations/external>`__
libraries. We plan to add support 
for widely used languages in the following libraries:

* ``NumPy``
* ``SciPy``
* ``Pandas``

* ``SciKit-Learn``
* ``PyTorch``
* ``TensorFlow``
* ``XGboost``
* ``Keras``

* ``Matplotlib``
* ``Seaborn``
* ``Bokeh``
* ``Plotly``
* ``pydot``

* ``Presto``

* ``Scrapy``
* ``BeautifulSoup``

So the rest of the libraries not mentioned are not yet supported or on our roadmap.



How to contribute to library specs
----------------------------------

There are a long tail of libraries that data scientists could be using, and we
would love to get community support for adding new annotations.

The module :mod:`lineapy.instrumentation` contains all the annotation types we support,
along with examples library calls and yaml annotations. We recommend that you start viewing from the top-level entry point
is :class:`~lineapy.instrumentation.annotation_spec.ModuleAnnotation`, to see how the different parts work together.

With yaml, you need to be careful with the indentations levels which could get
confusing. You can run the following bash script (from root): ``
./tests/tools/test_validate_annotation_spec.py`` to test the annotations you added. It would also be easier to copy off from `existing instrumentations <https://github.com/LineaLabs/lineapy/blob/main/lineapy/annotations/external>`__.

*If there are any syntax that the existing instrumentation doesn't support*,
please `file an issue on GitHub <https://github.com/LineaLabs/lineapy/issues/new?assignees=&labels=bug%2C+alpha-user&template=bug_report.md&title=>`__,
with the library you are using and the mutation/side effects documented.


