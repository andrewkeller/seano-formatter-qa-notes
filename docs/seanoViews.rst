Stock ``seano`` Views
====================

Zarf ships with a number of :doc:`seano` views that other projects may use to manufacture standardized documentation.

.. note::

    Not all views are for everyone.  Most views are designed to solve specific problems.

    People who work in projects: you should never feel pressured to use a view just because it exists here in Zarf.

    People who add views to Zarf: be specific about what problem the view is trying to solve so that other people
    working in projects can have an understanding of whether or not that view is good/bad for them to use.

QA Notes
--------

Target Problem
^^^^^^^^^^^^^^

Your release cycle is so long that by the time QA gets a build for testing/release, it's easy to forget some of the
initial changes that were made.

When you forget changes, a number of things happen:

* QA forgets to test things, which can lead to bugs getting released
* Product Managers forget to inform Customer Service of changes
* When bugs are released for changes that nobody remembered, a project can look disorganized or unreliable

QA Notes Workflow
^^^^^^^^^^^^^^^^^

The QA Notes view is an implementation of time travel.  Hear me out; it's not as crazy as it sounds.

At time of development, a developer writes testing notes in ``seano``.  The notes written should be as thorough as is
reasonable; you should always assume that all of your memory will be erased by the time QA sees these changes.

Later, when QA gets a build, the build includes a compiled HTML file containing all the notes written in this release.
When QA goes to look at the build, they also look at the QA Notes, and they have all of the best past versions of you
talking to them at once, in exquisite detail.

QA Notes Schema
^^^^^^^^^^^^^^^

The QA Notes view demands the following keys in each note.  All of the keys are optional; if one of the keys is not
applicable to the change, drop the entire key from the note.  You probably don't want to ever drop
``employee-short-loc-hlist-rst``, because that value is used as the title of the change in a lot of views.

All of these keys are included in the default ``seano`` note template, so you don't have to remember them.

.. code-block:: yaml

    ---
    tickets:
    - URL to JIRA/Redmine ticket

    customer-short-loc-hlist-rst:
      en-US:
      - Short sentence explaining this change to CE customers
      - "This is an hlist, which means:":
        - you can express a hierarchy here
      - This text usually comes from the ``#workroom-releasenotes`` channel in Slack

    employee-short-loc-hlist-rst:
      en-US:
      - Short sentence explaining this change to CE employees
      - "This is an hlist, which means:":
        - you can express a hierarchy here
      - This text usually comes from the developer who made the change
      - "For consistency, use imperative tense, without a full stop, such as:":
        - Cook the bacon
        - Don't crash when bacon is not loaded
        - You usually only need one line; these are just examples

    employee-technical-loc-rst:
      en-US: |
        Explain:

        * what changed
        * what might go wrong (risks)
        * how to resolve forseen problems
        * what this change means for the future of this project

        Target audience is Ops, and future developers, including your future self.

        This field is a single large reStructuredText blob.  Go wild.  Explaining details is good.

    employee-testing-loc-rst:
      en-US: |
        Explain what needs to be tested (new things to test) and/or re-tested (impact requiring regression testing).
        Target audience is QA.

        In addition to informing QA of what to test/re-test, this field also is used by QA as a "diff" to be applied
        to their official test plans.

        This field is a single large reStructuredText blob.  Go wild.  Explaining details is good.

Generating QA Notes
^^^^^^^^^^^^^^^^^^^

The recommended way to cause a QA Notes page to be generated in your project is to create a file called
``docs/qa-notes/wscript_build`` in your project, and add the following code to it:

.. code-block:: python
   :caption: ``docs/qa-notes/wscript_build``

   bld.compile_qa_notes()

The next time you run a build, QA Notes will be created at ``build/docs/qa-notes/qa-notes.html``.

``bld.compile_qa_notes()`` returns a Waf Node pointing to the output file.  If you want a standard Waf way to consume
the generated ``qa-notes.html`` file, that's it.

Alternatively, QA Notes may be manually created using ``seano format``:

.. code-block:: text

    $ wafexec seano format --src - --out - --format qa-notes < build/docs/seano-db-export.json
