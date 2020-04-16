Integration with other tools
============================
Call CLI from code
------------------
.. code-block:: python

   from plshandle import cli

   result = cli(["-m", "module.py"])

The returned structure contains parsed CLI arguments, collected modules, collected contracts
and contract check results which all can be used for further processing.

.. note::
   The ``cli()`` function does not print anything itself. However, if you provide invalid CLI
   arguments, the stdlib ``argparse`` module prints something and ``result.help_requested``
   will be set to ``True``.

Exit codes
----------
If you're calling plshandle using ``python -m plshandle``, the following exit codes are available:

====== ====================================================================
Code   Reason
====== ====================================================================
0      Contracts defined, used and checked; no contract violations
1      Contracts defined, used and checked; at least one contract violation
10     No modules collected
11     No contracts defined
12     Contracts defined, but none used
20     Help requested or invalid CLI arguments
21     Version requested
====== ====================================================================

Machine-readable results
------------------------
Passing the ``--json`` option prints a JSON array containing all check results (failed *and* passed) to ``stdout``.
This is guaranteed to be the only content in stdout if ``--verbose`` is not passed. Errors are still printed to
``stderr``.
