import logging

from gui_factory import handle_gui_error


def test_custom_decorator(caplog):
    class Dummy:
        def __init__(self):
            self.error_message_args = None

        def error_message(self, title, text):
            self.error_message_args = (title, text)

        @handle_gui_error("Ошибка в GUI")
        def faulty_method(self):
            raise ValueError("Тестовая Ошибка")

    obj = Dummy()

    with caplog.at_level(logging.ERROR):
        obj.faulty_method()

    assert "Ошибка в GUI: Тестовая Ошибка" in caplog.text
    assert isinstance(obj.error_message_args, tuple)
    assert obj.error_message_args[0] == "Ошибка:"
    assert "Тестовая Ошибка" in obj.error_message_args[1]
