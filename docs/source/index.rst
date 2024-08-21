
Clios
=====
Clios, create chainable command line operators

Installation
------------
.. termynal::
   :input: pip install clios
   :progress:
   

Example: ``numbers.py``
------------------------

Let's create a dumb CLI app ``numbers.py`` using `Clios` to do some basic arithematic on integer data. 

First, import the `Clios` class and create an instance, we call this an `app`:

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :start-after: [start]
   :end-before: [app_created]

Next, define a function that takes a single string as input and returns an integer. Use the app.reader decorator to register this function as a Reader for the int type:

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :pyobject: reader_int

In a `Clios` CLI application, a `Reader` is responsible for converting a string argument to the required data type, such as converting a string to an integer or processing a file path and returning its content.

Next, define a function which takes a single argument of type 'int' and prints the output. The `app.writer` decorator registers this function as `Writer` for type 'int':

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :pyobject: writer_int

A `Writer` is responsible for handling the output of a command, displaying it or writing it to a file (which will be covered later).

Now, lets define some operators:

Define a function that adds two integers and register it as an `Operator`:

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :pyobject: add

lets, define another function that subtracts one integer from another and register it as an `Operator`:

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :pyobject: sub

Define a function that sums a list of integers and register it as an `Operator`, with a custom name `sum`:

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :pyobject: sum_int

Finally, set up the application to parse command-line arguments and execute the corresponding commands:

.. literalinclude:: ../../examples/numbers/numbers.py
   :language: python
   :start-after: [main_start]
   :end-before: [main_end]


Now lets try the `numbers.py`:

.. example2termynal:: numbers.py examples.numbers.parameters



.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:






