Classes
=======
Supported special methods
-------------------------

- ``__init__``
- ``__call__``

Subclasses
----------
Contracts defined in subclasses work as expected:

.. code-block:: python

   class Base:
       @plshandle(SomeError)
       def __init__(self):
           pass

       @plshandle(SomeError)
       def method(self):
           pass

   class Parent(Base):
      pass

   var: Parent = Parent()  # resolved as Base.__init__, contract is checked
   var.method()  # resolved as Base.method, contract is checked

Pitfalls
--------

-  mypy does not infer the return type of ``Class.__init__`` as ``Class`` (which is technically correct).
   Therefore, make sure to help mypy and annotate the type:

   .. code-block:: python

      # var = Class() does not work!
      var: Class = Class()
      var.method()

   Since plshandle supports special call expression patterns, the following works without any "hacks":

   .. code-block:: python

      Class()  # __init__
      Class()()  # __call__
      Class().inst_method()
      Class.class_method()

