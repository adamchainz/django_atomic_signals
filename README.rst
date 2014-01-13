django_atomic_signals - Signals for atomic transaction blocks in Django
============================================================================

.. image:: https://travis-ci.org/nickbruun/django_atomic_signals.png?branch=master
        :target: https://travis-ci.org/nickbruun/django_atomic_signals

By default, Django does not provide signals for when a database transaction is entered or left. As per various Django tickets, there seems to be no interest in adding this, which has led to a variety of third party solutions. However, due to the changes to transaction handling in Django 1.6, these solutions are no longer functional.

``django_atomic_signals`` provides a Django 1.6 compatible approach to transaction signals through a monkey patching of the ``django.db.transactions.Atomic`` context manager.


Installation
------------

To install ``django_atomic_signals``, do yourself a favor and don't use anything other than `pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

   $ pip install django-atomic-signals

Add ``django_atomic_signals`` to the list of installed apps in your settings file:

.. code-block:: python

   INSTALLED_APPS = (
       'django_atomic_signals',
       ..
   )


Usage
-----

``django_atomic_signals`` provides four signals for applications to use:

``django_atomic_signals.pre_enter_atomic_block``
   Emitted prior to attempting to enter an atomic transaction block.

   :Parameters:
     * ``using`` -- Database alias being used for the transaction.
     * ``outermost`` -- Boolean value indicating whether or not the transaction is the outermost transaction, ie. if the transaction will be effectively committed once the transaction is successfully exited.
     * ``savepoint`` -- Boolean value indicating whether or not the atomic block is a savepoint, ie. if the transaction causes a savepoint to be created.

``django_atomic_signals.post_enter_atomic_block``
   Emitted after an atomic transaction block has been entered.

   :Parameters:
     * ``using`` -- Database alias being used for the transaction.
     * ``outermost`` -- Boolean value indicating whether or not the transaction is the outermost transaction, ie. if the transaction will be effectively committed once the transaction is successfully exited.
     * ``savepoint`` -- Boolean value indicating whether or not the atomic block is a savepoint, ie. if the transaction causes a savepoint to be created.

``django_atomic_signals.pre_exit_atomic_block``
   Emitted prior to attempting to exit an atomic transaction block.

   :Parameters:
     * ``using`` -- Database alias being used for the transaction.
     * ``outermost`` -- Boolean value indicating whether or not the transaction is the outermost transaction, ie. if the transaction will be effectively committed once the transaction is successfully exited.
     * ``savepoint`` -- Boolean value indicating whether or not the atomic block is a savepoint, ie. if the transaction causes a savepoint to be created.
     * ``successful`` -- Boolean value indicating whether or not the database actions within the transaction block were successful.

``django_atomic_signals.post_exit_atomic_block``
   Emitted after an atomic transaction block has been exited.

   :Parameters:
     * ``using`` -- Database alias being used for the transaction.
     * ``outermost`` -- Boolean value indicating whether or not the transaction is the outermost transaction, ie. if the transaction will be effectively committed once the transaction is successfully exited.
     * ``savepoint`` -- Boolean value indicating whether or not the atomic block is a savepoint, ie. if the transaction causes a savepoint to be created.
     * ``successful`` -- Boolean value indicating whether or not the database actions within the transaction block as well as the attempt to commit the changes to the database were successful.
