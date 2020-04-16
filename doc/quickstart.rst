Quickstart
==========

.. toctree::
   :maxdepth: 2
   :caption: Quickstart

Install plshandle
-----------------
.. code-block:: sh

   pip install plshandle

Create a contract
-----------------
.. code-block:: python

   # module1.py
   from plshandle import plshandle

   @plshandle(FileNotFoundError)
   def parse_something(file):
       with open(file, "r") as fp:
           return fp.read()

   # module2.py
   from module1 import parse_something

   parse_something("foobar.txt")

Check for contract violations
-----------------------------
.. code-block:: sh

   python -m plshandle -m module1.py -m module2.py

   module2.py:3: Violated contract of module1.parse_something. Not handled nor propagated builtins.FileNotFoundError


Fix the contract violation
--------------------------
.. code-block:: python

   try:
       parse_something("foobar.txt")
   except FileNotFoundError:
       pass

.. code-block:: sh

   python -m plshandle -m module1.py -m module2.py
