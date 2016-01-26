django_atomic_signals - Signals for atomic transaction blocks in Django
============================================================================

.. image:: https://travis-ci.org/adamchainz/django_atomic_signals.png?branch=master
        :target: https://travis-ci.org/adamchainz/django_atomic_signals

Don't Use This Package
----------------------

When this library was created, there was an unmet demand for its main use case: being able to run code when the current
transaction commits, and only if it commits. However, signals are not the best way to do this, as Django core developer
Aymeric Augustin has covered on his `django-transaction-signals
<https://github.com/aaugustin/django-transaction-signals>`_ project (which is very similar to this one). You can read
more explanation and history there.

If you want a supported method of running a function on commit, then:

- on Django >= 1.9, use the built-in on_commit_ hook
- on Django < 1.9, use `django-transaction-hooks`_ (the original source of 1.9's ``on_commit``)

.. _on_commit: https://docs.djangoproject.com/en/dev/topics/db/transactions/#django.db.transaction.on_commit
.. _django-transaction-hooks: https://django-transaction-hooks.readthedocs.org/

For other usecases, read Aymeric's description of possible solutions.

If your project is still using this library, please migrate.

The current version of `django-atomic-signals`, 2.0.0, simply errors upon import, directing you here.
