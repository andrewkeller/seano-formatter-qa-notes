QA Notes Formatter Plugin for Seano
===================================

This project provides a Seano formatter named "QA Notes" which, given a query of
a Seano database, will generate a self-contained single-file HTML file
presenting an overview of what changes need Quality Assurance (QA) attention.

Intended Use Cases
------------------

The intended use case of this Seano View is one where it is easy to forget to
tell QA of one or more changes in the build you just sent them.  This can happen
because you spent a month working on a single feature and your memory is fuzzy
on the early parts, or because you have multiple coworkers and you aren't an
expert in what they did.  Regardless of why you forgot to tell QA about some
details, the common risks include:

1.  QA can miss bugs, leading to the bugs reaching production
1.  Product Managers can forget to inform other departments of changes
1.  UX and/or Marketing can forget to inform customers of changes
1.  When customers notice changes before employees do, it can make the project
    look disorganized or unreliable.

Typical Workflow
----------------

At time of development, a developer writes testing notes in Seano.  The notes
should be as thorough as reasonable: assume you might be on vacation when QA is
reading it.

Later, when QA gets a build, the build includes a machine-written HTML file
containing all of the testing notes written in this release, colloquially called
_the QA Notes_.  QA reads these notes to know what to test.

Schema
------

The QA Notes view uses this schema for notes:

```yaml
---
# (OPTIONAL) URLs to an external ticketing system
tickets:
- https://example.com/tickets/EXAMPLE-1234

# (OPTIONAL) Customer-facing short release notes
customer-short-loc-hlist-md: # (or `customer-short-loc-hlist-rst` for RST)
  en-US:
  - Short sentence explaining this change to customers
  - "This is an hlist, which means:":
    - you can express a hierarchy here

# (REQUIRED) Employee-facing short release notes
employee-short-loc-hlist-md: # (or `employee-short-loc-hlist-rst` for RST)
  en-US:
  - Short sentence explaining this change to employees
  - "This is an hlist, which means:":
    - you can express a hierarchy here

# (OPTIONAL) Employee-facing long technical discussion
employee-technical-loc-md: # (or `employee-technical-loc-rst` for RST)
  en-US: |
    What was the problem?  What solutions did you reject?  Why did you choose
    this solution?  What might go wrong?  What can Ops do to resolve an outage
    over the weekend?

    This field is a single large Markdown blob.  Explaining details is good.

# (OPTIONAL) Customer Service-facing long technical discussion
mc-technical-loc-md:  # (or `mc-technical-loc-rst` for RST)
  en-US: |
    What was the problem?  What is the solution?  What might go wrong?  How can
    Customer Service fix a problem over the weekend?

    This field is a single large Markdown blob.  Remember that Customer Service
    watches over many products; be specific, but also be terse.

# (REQUIRED) QA-facing long technical discussion
qa-technical-loc-md:  # (or `qa-technical-loc-rst` for RST)
  en-US: |
    What new features need to be tested?  What old features need to be
    regression-tested?

    QA uses this section to perform QA, and also as a "diff" to update their
    own test plan archives.

    This field is a single large Markdown blob.  Explaining details is good.
    Assume that QA has zero knowledge of *what* to test, but that given that
    knowledge, they know *how* to test it.  Be specific in descriptions;
    avoid generalizations when practical.  Be as technical as you want.
    If QA has questions, they'll ask you.
```

Testing Locally
---------------

Starting from scratch, this is how to set up local unit testing:

```sh
# Create and enter a virtual environment:
virtualenv .venv
. .venv/bin/activate

# Install this Seano formatter plugin in the virtual environment in "editable mode"
pip install -e .

# Install extra dependencies needed by the unit tests:
pip install -r ci_utest_requirements.txt
```

Then, going forward, you can run unit tests like this:

```sh
pytest
```
