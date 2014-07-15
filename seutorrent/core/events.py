"""
events.py

This module handles the event API for seutorrent core. Arbitrary code can
listen to engine events in order to drive UI changes or other engine behaviors.

"""

from uuid import uuid1


class EventEmitter:
    """Implementation of the observer pattern."""

    def __init__(self, event_name):
        self.event_name = event_name
        self.listeners = {}

    def add_event_listener(self, func):
        new_listener_id = str(uuid1())
        self.listeners[new_listener_id] = func
        return new_listener_id

    def remove_event_listener(self, listener_id):
        if listener_id in self.listeners:
            del(self.listeners[listener_id])

    def emit_event(self, *args):
        for l_id, listener in self.listeners.items:
            try:
                listener(*args)
            except BaseException, e:
                # Error listener should not call itself to avoid loops
                if self.event_name != 'error':
                    err_msg = "Error running %s listener %s: %s" % (
                        self.event_name, l_id, e.message)
                    on_error.emit_event(err_msg)


on_error = EventEmitter('error')
on_warning = EventEmitter('warning')
on_torrent_started = EventEmitter('torrent_started')
on_torrent_stopped = EventEmitter('torrent_stopped')
on_torrent_completed = EventEmitter('torrent_completed')
