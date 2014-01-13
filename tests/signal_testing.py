from __future__ import absolute_import

from django.db import DEFAULT_DB_ALIAS
from django_atomic_signals import (
    pre_enter_atomic_block, post_enter_atomic_block,
    pre_exit_atomic_block, post_exit_atomic_block,
)


class AtomicSignalCall(object):
    """Atomic signal call.
    """

    def __init__(self,
                 signal,
                 outermost,
                 successful=None,
                 savepoint=True,
                 using=DEFAULT_DB_ALIAS):
        self.signal = signal
        self.outermost = outermost
        self.savepoint = savepoint
        self.successful = successful
        self.using = DEFAULT_DB_ALIAS if using is None else using

    def to_tuple(self):
        return (self.signal, self.outermost, self.savepoint, self.successful,
                self.using)

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        return self.to_tuple() != other.to_tuple()

    def __repr__(self):
        return '<AtomicSignalCall: %s, outermost = %r, savepoint = %r, ' \
            'successful = %r, using = %r>' % ({
                pre_enter_atomic_block: 'pre enter',
                post_enter_atomic_block: 'post enter',
                pre_exit_atomic_block: 'pre exit',
                post_exit_atomic_block: 'post exit',
            }[self.signal], self.outermost, self.savepoint, self.successful,
                self.using)


class AtomicBlockReceiver(object):
    """Testing receiver for atomic transaction block signals.

    :ivar calls:
        :class:`list` of :class:`AtomicSignalCall` instances. For entering
        signals, ``successful`` will be ``None``.
    """

    signals = [
        pre_enter_atomic_block,
        post_enter_atomic_block,
        pre_exit_atomic_block,
        post_exit_atomic_block,
    ]

    def __init__(self):
        self.calls = []

    def __call__(self, signal, sender, using, outermost, savepoint, **kwargs):
        self.calls.append(AtomicSignalCall(signal,
                                           outermost,
                                           kwargs.pop('successful', None),
                                           savepoint,
                                           using))

    def connect(self):
        """Connect all atomic transaction block signals to the receiver.
        """

        for signal in self.signals:
            signal.connect(self)

    def disconnect(self):
        """Disconnect all atomic transaction block signals from the receiver.
        """

        for signal in self.signals:
            signal.disconnect(self)


def create_model_atomic_signal_call_sequence():
    """Atomic signal call sequence for model creation.

    Utility method for describing the call sequence for the often used model
    instance creation call in the atomic test case:

    .. code-block: python

       Reporter.objects.create(..)

    :returns: a :class:`list` of :class:`AtomicSignalCall` instances.
    """

    return [
        AtomicSignalCall(pre_enter_atomic_block, False, savepoint=False),
        AtomicSignalCall(post_enter_atomic_block, False, savepoint=False),
        AtomicSignalCall(pre_exit_atomic_block, False, True, savepoint=False),
        AtomicSignalCall(post_exit_atomic_block, False, True, savepoint=False),
    ]


def enter_block_atomic_signal_call_sequence(outermost=True, savepoint=True):
    """Atomic signal call sequence for entering an atomic transaction block.

    :param outermost:
        Whether the transaction block is the outermost. Default ``True``.
    :param savepoint:
        Whether the transaction block uses a save point. Default ``True``.
    :returns: a :class:`list` of :class:`AtomicSignalCall` instances.
    """

    return [
        AtomicSignalCall(pre_enter_atomic_block, outermost,
                         savepoint=savepoint),
        AtomicSignalCall(post_enter_atomic_block, outermost,
                         savepoint=savepoint),
    ]


def leave_block_atomic_signal_call_sequence(outermost=True,
                                            successful=True,
                                            savepoint=True):
    """Atomic signal call sequence for leaving an atomic transaction block.

    :param outermost:
        Whether the transaction block is the outermost. Default ``True``.
    :param successful:
        Whether the transaction block was successful and thus committed.
        Default ``True``.
    :param savepoint:
        Whether the transaction block uses a save point. Default ``True``.
    :returns: a :class:`list` of :class:`AtomicSignalCall` instances.
    """

    return [
        AtomicSignalCall(pre_exit_atomic_block, outermost, successful,
                         savepoint=savepoint),
        AtomicSignalCall(post_exit_atomic_block, outermost, successful,
                         savepoint=savepoint),
    ]
