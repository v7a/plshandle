Aliases
=======

plshandle supports aliases defined in the same module, e.g.:

.. code-block:: python

   from module import func as func_alias

   func_alias_2 = func_alias

   func_alias_2()  # will resolve to 'func'

and if you're one of those guys, you can also define a serious business alias for plshandle:

.. code-block:: python

   from plshandle import plshandle as serious_business

   @serious_business(KeyError)
   def func():
       ...
