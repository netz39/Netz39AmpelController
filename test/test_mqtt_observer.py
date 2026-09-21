from unittest.mock import Mock

from MqttObserver import MqttObserver


def test_is_loop_running_with_alive_thread():
    observer = object.__new__(MqttObserver)
    observer.client = Mock()
    observer.client._thread = Mock()
    observer.client._thread.is_alive.return_value = True

    assert observer.is_loop_running() is True


def test_is_loop_running_without_thread():
    observer = object.__new__(MqttObserver)
    observer.client = Mock()
    observer.client._thread = None

    assert observer.is_loop_running() is False


def test_is_loop_running_with_dead_thread():
    observer = object.__new__(MqttObserver)
    observer.client = Mock()
    observer.client._thread = Mock()
    observer.client._thread.is_alive.return_value = False

    assert observer.is_loop_running() is False
