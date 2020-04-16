Exception propagation
=====================
Similar to Java, exceptions can be propagated to the caller. Whenever plshandle encounters
a function call forming a contract and determines that one of its exceptions is not handled, it
traverses the scope upwards and checks if the current function also defines a contract with
one or more of the exceptions to be handled in this call:

.. code-block:: python

   @plshandle(KeyError, AttributeError)
   def foo():
      pass

   @plshandle(KeyError)
   def bar():
      foo()  # AttributeError is reported as not handled, KeyError is reported as propagated
