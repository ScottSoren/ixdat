Instructions
============

Use this as a staging ground for CHANGES.rst. In other words, describe the
changes and additions to ixdat's API associated with your contribution. The idea is
that what you write here informs other developers what is on its way and then will be
copied to CHANGES.rst when the next version of ixdat is distributed. Please include
links to relevant Issues, Discussions, and PR's on github with the following format
(replace XX):

`Issue #XX <https://github.com/ixdat/ixdat/issues/XX>`_
`PR #XX <https://github.com/ixdat/ixdat/pull/XX>`_

For ixdat 0.4.1
===============

development_scripts
^^^^^^^^^^^^^^^^^^^

- The demos have moved to the new ``ixdat.demos`` package, grouped like ixdat into
  ``readers``, ``calculators`` and ``techniques``. Each demo has loader functions
  which return its ixdat objects, an ``EXAMPLES`` dictionary of these loaders, and a
  ``main(show=True)`` which plots the results and returns them as a dictionary. Other
  scripts import the loaders, e.g.
  ``from ixdat.demos.readers.demo_autolab_reader import load_single_file``.
  ``get_demo_data_dir()`` returns the demo data folder, given by the environment
  variable ``IXDAT_DEMO_DATA_DIR`` or ``demo_data/`` in the repository root.
  ``development_scripts/save_all_demo_data_in_sqlite.py`` saves every demo example
  in an SQLite file and shows its tables in a browser.
  `PR #212 <https://github.com/ixdat/ixdat/pull/212>`_
