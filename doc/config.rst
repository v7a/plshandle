Configuration file
==================
A configuration file can be specified using the ``--config`` CLI option. If this option is not provided,
plshandle looks for settings in file ``./pyproject.toml``. These settings are then merged with CLI arguments.

Format
------
The config file must be in TOML format defining a section called ``tool.plshandle``:

.. code-block:: ini

   [tool.plshandle]
   directories = ["dir1", "dir2", ...]
   packages = ["pkg1", "pkg2", ...]
   modules = ["mod1", "mod2", ...]
   strict = true|false
   verbose = true|false
   json = true|false
