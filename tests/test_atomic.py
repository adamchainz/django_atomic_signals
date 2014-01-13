from __future__ import absolute_import

from django.db import connection, transaction, DatabaseError
from django.test import TransactionTestCase
from django.utils import six
from django.utils.unittest import skipIf, skipUnless

from .models import Reporter
from .signal_testing import (
    AtomicBlockReceiver,
    create_model_atomic_signal_call_sequence,
    enter_block_atomic_signal_call_sequence,
    leave_block_atomic_signal_call_sequence,
)


@skipUnless(connection.features.uses_savepoints,
            "'atomic' requires transactions and savepoints.")
class AtomicTests(TransactionTestCase):
    """
    Tests for the atomic decorator and context manager.

    The tests make assertions on internal attributes because there isn't a
    robust way to ask the database for its current transaction state.

    Since the decorator syntax is converted into a context manager (see the
    implementation), there are only a few basic tests with the decorator
    syntax and the bulk of the tests use the context manager syntax.
    """

    def setUp(self):
        super(AtomicTests, self).setUp()
        self.atomic_block_receiver = AtomicBlockReceiver()
        self.atomic_block_receiver.connect()

    def tearDown(self):
        self.atomic_block_receiver.disconnect()
        super(AtomicTests, self).tearDown()

    def assertAtomicSignalCalls(self, calls):
        """Assert a certain order of atomic signal calls.
        """

        self.assertListEqual(self.atomic_block_receiver.calls, calls)

    def assertAtomicSignalCallsForCommit(self):
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, True)
        )

    def assertAtomicSignalCallsForRollback(self):
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_decorator_syntax_commit(self):
        @transaction.atomic
        def make_reporter():
            Reporter.objects.create(first_name="Tintin")
        make_reporter()
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Tintin>'])
        self.assertAtomicSignalCallsForCommit()

    def test_decorator_syntax_rollback(self):
        @transaction.atomic
        def make_reporter():
            Reporter.objects.create(first_name="Haddock")
            raise Exception("Oops, that's his last name")
        with six.assertRaisesRegex(self, Exception, "Oops"):
            make_reporter()
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCallsForRollback()

    def test_alternate_decorator_syntax_commit(self):
        @transaction.atomic()
        def make_reporter():
            Reporter.objects.create(first_name="Tintin")
        make_reporter()
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Tintin>'])
        self.assertAtomicSignalCallsForCommit()

    def test_alternate_decorator_syntax_rollback(self):
        @transaction.atomic()
        def make_reporter():
            Reporter.objects.create(first_name="Haddock")
            raise Exception("Oops, that's his last name")
        with six.assertRaisesRegex(self, Exception, "Oops"):
            make_reporter()
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCallsForRollback()

    def test_commit(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Tintin>'])
        self.assertAtomicSignalCallsForCommit()

    def test_rollback(self):
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with transaction.atomic():
                Reporter.objects.create(first_name="Haddock")
                raise Exception("Oops, that's his last name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCallsForRollback()

    def test_nested_commit_commit(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
            with transaction.atomic():
                Reporter.objects.create(first_name="Archibald",
                                        last_name="Haddock")
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Archibald Haddock>',
                                  '<Reporter: Tintin>'])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, True) +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, True)
        )

    def test_nested_commit_rollback(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
            with six.assertRaisesRegex(self, Exception, "Oops"):
                with transaction.atomic():
                    Reporter.objects.create(first_name="Haddock")
                    raise Exception("Oops, that's his last name")
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Tintin>'])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(False, False) +

            # Leave atomic transaction block with exception caught.
            leave_block_atomic_signal_call_sequence(True, True)
        )

    def test_nested_rollback_commit(self):
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with transaction.atomic():
                Reporter.objects.create(last_name="Tintin")
                with transaction.atomic():
                    Reporter.objects.create(last_name="Haddock")
                raise Exception("Oops, that's his first name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, True) +

            # Leave atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_nested_rollback_rollback(self):
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with transaction.atomic():
                Reporter.objects.create(last_name="Tintin")
                with six.assertRaisesRegex(self, Exception, "Oops"):
                    with transaction.atomic():
                        Reporter.objects.create(first_name="Haddock")
                    raise Exception("Oops, that's his last name")
                raise Exception("Oops, that's his first name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block with caught eexception.
            leave_block_atomic_signal_call_sequence(False, True) +

            # Leave atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_merged_commit_commit(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
            with transaction.atomic(savepoint=False):
                Reporter.objects.create(first_name="Archibald",
                                        last_name="Haddock")
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Archibald Haddock>',
                                  '<Reporter: Tintin>'])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False, savepoint=False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block with caught eexception.
            leave_block_atomic_signal_call_sequence(False, True,
                                                    savepoint=False) +

            # Leave atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(True, True)
        )

    def test_merged_commit_rollback(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
            with six.assertRaisesRegex(self, Exception, "Oops"):
                with transaction.atomic(savepoint=False):
                    Reporter.objects.create(first_name="Haddock")
                    raise Exception("Oops, that's his last name")
        # Writes in the outer block are rolled back too.
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False, savepoint=False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, False,
                                                    savepoint=False) +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_merged_rollback_commit(self):
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with transaction.atomic():
                Reporter.objects.create(last_name="Tintin")
                with transaction.atomic(savepoint=False):
                    Reporter.objects.create(last_name="Haddock")
                raise Exception("Oops, that's his first name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False, savepoint=False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, True,
                                                    savepoint=False) +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_merged_rollback_rollback(self):
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with transaction.atomic():
                Reporter.objects.create(last_name="Tintin")
                with six.assertRaisesRegex(self, Exception, "Oops"):
                    with transaction.atomic(savepoint=False):
                        Reporter.objects.create(first_name="Haddock")
                    raise Exception("Oops, that's his last name")
                raise Exception("Oops, that's his first name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False, savepoint=False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, True,
                                                    savepoint=False) +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_reuse_commit_commit(self):
        atomic = transaction.atomic()
        with atomic:
            Reporter.objects.create(first_name="Tintin")
            with atomic:
                Reporter.objects.create(first_name="Archibald",
                                        last_name="Haddock")
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Archibald Haddock>',
                                  '<Reporter: Tintin>'])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, True) +

            # Leave atomic transaction block.
            leave_block_atomic_signal_call_sequence(True, True)
        )

    def test_reuse_commit_rollback(self):
        atomic = transaction.atomic()
        with atomic:
            Reporter.objects.create(first_name="Tintin")
            with six.assertRaisesRegex(self, Exception, "Oops"):
                with atomic:
                    Reporter.objects.create(first_name="Haddock")
                    raise Exception("Oops, that's his last name")
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Tintin>'])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(False, False) +

            # Leave atomic transaction block with exception caught.
            leave_block_atomic_signal_call_sequence(True, True)
        )

    def test_reuse_rollback_commit(self):
        atomic = transaction.atomic()
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with atomic:
                Reporter.objects.create(last_name="Tintin")
                with atomic:
                    Reporter.objects.create(last_name="Haddock")
                raise Exception("Oops, that's his first name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block.
            leave_block_atomic_signal_call_sequence(False, True) +

            # Leave atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_reuse_rollback_rollback(self):
        atomic = transaction.atomic()
        with six.assertRaisesRegex(self, Exception, "Oops"):
            with atomic:
                Reporter.objects.create(last_name="Tintin")
                with six.assertRaisesRegex(self, Exception, "Oops"):
                    with atomic:
                        Reporter.objects.create(first_name="Haddock")
                    raise Exception("Oops, that's his last name")
                raise Exception("Oops, that's his first name")
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter nested atomic transaction block.
            enter_block_atomic_signal_call_sequence(False) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave nested atomic transaction block with caught eexception.
            leave_block_atomic_signal_call_sequence(False, True) +

            # Leave atomic transaction block with exception.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_force_rollback(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
            # atomic block shouldn't rollback, but force it.
            self.assertFalse(transaction.get_rollback())
            transaction.set_rollback(True)
        self.assertQuerysetEqual(Reporter.objects.all(), [])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Leave atomic transaction with forced rollback.
            leave_block_atomic_signal_call_sequence(True, False)
        )

    def test_prevent_rollback(self):
        with transaction.atomic():
            Reporter.objects.create(first_name="Tintin")
            sid = transaction.savepoint()
            # trigger a database error inside an inner atomic without savepoint
            with self.assertRaises(DatabaseError):
                with transaction.atomic(savepoint=False):
                    connection.cursor().execute(
                        "SELECT no_such_col FROM transactions_reporter"
                    )
            # prevent atomic from rolling back since we're recovering manually
            self.assertTrue(transaction.get_rollback())
            transaction.set_rollback(False)
            transaction.savepoint_rollback(sid)
        self.assertQuerysetEqual(Reporter.objects.all(),
                                 ['<Reporter: Tintin>'])
        self.assertAtomicSignalCalls(
            # Enter atomic transaction block.
            enter_block_atomic_signal_call_sequence(True) +

            # Create Reporter.
            create_model_atomic_signal_call_sequence() +

            # Enter and leave atomic transaction block.
            enter_block_atomic_signal_call_sequence(False, savepoint=False) +
            leave_block_atomic_signal_call_sequence(False, False,
                                                    savepoint=False) +

            # Leave atomic transaction with recovered rollback.
            leave_block_atomic_signal_call_sequence(True, True)
        )


class AtomicInsideTransactionTests(AtomicTests):
    def setUp(self):
        super(AtomicInsideTransactionTests, self).setUp()

    def tearDown(self):
        super(AtomicInsideTransactionTests, self).tearDown()


@skipIf(connection.features.autocommits_when_autocommit_is_off,
        "This test requires a non-autocommit mode that doesn't autocommit.")
class AtomicWithoutAutocommitTests(AtomicTests):
    def setUp(self):
        super(AtomicWithoutAutocommitTests, self).setUp()
        transaction.set_autocommit(False)

    def tearDown(self):
        # The tests access the database after exercising 'atomic', initiating
        # a transaction ; a rollback is required before restoring autocommit.
        transaction.rollback()
        transaction.set_autocommit(True)
        super(AtomicWithoutAutocommitTests, self).tearDown()


@skipIf(connection.features.autocommits_when_autocommit_is_off,
        "This test requires a non-autocommit mode that doesn't autocommit.")
class AtomicInsideLegacyTransactionManagementTests(AtomicTests):

    def setUp(self):
        super(AtomicInsideLegacyTransactionManagementTests, self).setUp()
        transaction.enter_transaction_management()

    def tearDown(self):
        # The tests access the database after exercising 'atomic', making the
        # connection dirty; a rollback is required to make it clean.
        transaction.rollback()
        transaction.leave_transaction_management()
        super(AtomicInsideLegacyTransactionManagementTests, self).tearDown()
