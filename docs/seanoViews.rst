Stock ``seano`` Views
====================

Zarf ships with a number of :doc:`seano` views that other projects may use to manufacture standardized documentation.

.. note::

    Not all views are for everyone.  Most views are designed to solve specific problems.

    People who work in projects: you should never feel pressured to use a view just because it exists here in Zarf.

    People who add views to Zarf: be specific about what problem the view is trying to solve so that other people
    working in projects can have an understanding of whether or not that view is good/bad for them to use.

Group A Views
-------------

A number of views share similar schemas in ``seano``.  To make documentation easier to scan and compare, this
group of views are all documented here, all at once.

These views include:

* QA Notes *(standalone single-file HTML)*

Intended use cases
^^^^^^^^^^^^^^^^^^

* QA Notes

  Your release cycle is so long that by the time QA gets a build for testing/release, it's easy
  to forget some of the initial changes that were made.

  When you forget changes, a number of things happen:

  * QA forgets to test things, which can lead to bugs getting released
  * Product Managers forget to inform Member Care of changes
  * When bugs are released for changes that nobody remembered, a project can look disorganized
    or unreliable

  At time of development, a developer writes testing notes in ``seano``.  The notes written should
  be as thorough as is reasonable; you should always assume that all of your memory will be erased
  by the time QA sees these changes.

  Later, when QA gets a build, the build includes a compiled HTML file containing all the notes
  written in this release.  When QA goes to look at the build, they also look at the QA Notes, and
  they have all of the best past versions of you talking to them at once, in exquisite detail.


Schema
^^^^^^

The *Group A Views*, as a group, use this schema for release objects inside ``seano-config.yaml``.
Not every individual view in this group uses every part of this schema.  All of the keys are
optional; as general practice, if one of the keys is not applicable to the release, drop the
entire key from the release.

.. code-block:: yaml
   :caption: ``seano-config.yaml``

   releases: # The top-level releases list in seano-config.yaml

   - name: 1.2.3 # Declaration of example release

     employee-prologue-loc-rst:
       en-US: |
         You may type text into here that describes the release
         as a whole.  This field is typically printed directly
         above internal release notes.

     # Events are stupid -- *very stupid*.  They are an ordered
     # list of event names, with corresponding dates.  Both the
     # event names and dates are *arbitrary strings!*  The dates
     # are currently not parsed, but may be in the future.  The
     # event names are non-functional *except* that release
     # statuses have certain pre-set colors for certain event
     # names.  The colors can be customized.  You may have as
     # few or as many events as you want on a release.
     events:
     - public beta: 1/1/2021
     - general release: 1/10/2021


The *Group A Views*, as a group, use this schema for notes.  Not every individual view uses every
part of the schema.  All of the keys are optional; as general practice, if one of the keys is not
applicable to the change, drop the entire key from the note.  That said, the
``employee-short-loc-hlist-rst`` key is used as a title in a lot of views, so you probably don't
want to drop that one.

All of these keys are included in the default ``seano`` note template, so you don't have to remember them.

.. code-block:: yaml

    ---
    risk: One of low, medium, high; risk level does not factor in deployment tricks to lower risk.

    tickets:
    - URL to JIRA/Redmine ticket

    min-supported-os:        # Only include this section if you changed the minimum supported OS
      os1: "version number"  # You must specify all OSs every time you define a new value
      os2: "version number"  # OS versions should be quoted to avoid yaml assuming numeric type

    max-supported-os:        # Only include this section if you changed the maximum supported OS
      os1: "version number"  # You must specify all OSs every time you define a new value
      os2: "version number"  # OS versions should be quoted to avoid yaml assuming numeric type

    employee-milestones-list-loc-rst:
    - en-US: Short description of a big change
    - en-US: Use sparingly, because these are printed prominently

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
        You are talking to your future self and Ops.

        What was the problem?  What solutions did you reject?  Why did you choose
        this solution?  What might go wrong?  What can Ops do to resolve an outage
        over the weekend?

        This field is a single large reStructuredText blob.  Explaining details is
        good.

    mc-technical-loc-rst:
      en-US: |
        You are talking to a Tier-2 Member Care Representative.

        What changed?  How does this impact users?  How does this impact MC?

        Assume something *is going wrong*.  What caused it?  How can MC resolve it
        over the weekend?

        T2's have a dedicated block of time for catching up on release notes for
        all products at CE.  They oversee many products, so we try to keep this
        section as blunt and brief as is practical.  T2's are technically inclined,
        so feel free to use technical jargon to shorten explanations.

        Don't be afraid to be terse; if a T2 has questions, they'll often hop over
        to the ``employee-technical-loc-rst`` section to look for more details.

        Sometimes a screenshot is a great way to shorten an explanation:

        .. image:: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj4KICA8cGF0aCBkPSJNNTAsMzBjOS0yMiA0Mi0yNCA0OCwwYzUsNDAtNDAsNDAtNDgsNjVjLTgtMjUtNTQtMjUtNDgtNjVjIDYtMjQgMzktMjIgNDgsMCB6IiBmaWxsPSIjRjAwIiBzdHJva2U9IiMwMDAiLz4KPC9zdmc+
           :width: 100
           :alt: red heart with black outline

        If what you want to write here is identical to what you've already written
        in another section, you can use Yaml's reference syntax to copy another
        section.  You can copy any ``*-loc-rst`` field, or any ``*-loc-hlist-rst``
        field.  Example:

        .. code-block:: yaml

           employee-short-loc-hlist-rst: &empl-short
             en-US: #                    ^^^^^^^^^^^  Mark section to copy
             - Hello, this is an internal release note

           mc-technical-loc-rst: *empl-short
           #                     ^^^^^^^^^^^  Copy contents of the marked section

        If this change doesn't impact customers or Member Care, or is too obscure
        to mention, then delete this section.

    qa-technical-loc-rst:
      en-US: |
        You are talking to QA.

        What new features need to be tested?  What old features need to be
        regression-tested?

        QA uses this section to perform QA, and also as a "diff" to update their
        own test plan archives.

        This field is a single large reStructuredText blob.  Explaining details is
        good.  Assume that QA has zero knowledge of *what* to test, but that given
        that knowledge, they know *how* to test it.  Be specific in descriptions;
        avoid generalizations when practical.  Be as technical as you want.  If QA
        has questions, they'll ask you.


Generating Group A Views
^^^^^^^^^^^^^^^^^^^^^^^^

If you create all of the following files in your project, then a build of your project
will produce all of the Group A Views.

You do not need to compile all of these views for any of them to work.

.. code-block:: python
   :caption: ``docs/qa-notes/wscript_build``

   # Creates a file named `qa-notes.html`
   bld.compile_qa_notes()
