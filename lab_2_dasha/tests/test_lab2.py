# -*- coding: utf-8 -*-
"""
Тесты для лабораторной работы (задание из task.md, п. 3).
Запуск из корня проекта:
    python -m pytest tests/ -v          # наглядно: каждый тест и итог «N passed»
    python -m unittest discover -s tests -p "test_*.py" -v
"""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_APP_DIR = os.path.join(_ROOT, 'app')
sys.path.insert(0, _APP_DIR)

import app as flask_app_module  # noqa: E402

app = flask_app_module.app
DEMO_COOKIE_NAME = flask_app_module.DEMO_COOKIE_NAME
DEMO_COOKIE_VALUE = flask_app_module.DEMO_COOKIE_VALUE
ERR_PHONE_DIGITS = flask_app_module.ERR_PHONE_DIGITS
ERR_PHONE_CHARS = flask_app_module.ERR_PHONE_CHARS


class ParamsPageTests(unittest.TestCase):
    """Параметры URL — все переданные параметры отображаются."""

    def test_params_page_shows_all_query_string_parameters(self):
        with app.test_client() as c:
            rv = c.get('/params?city=Moscow&year=2026')
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('city', html)
            self.assertIn('Moscow', html)
            self.assertIn('year', html)
            self.assertIn('2026', html)

    def test_params_page_empty_query_shows_no_parameters_message(self):
        with app.test_client() as c:
            rv = c.get('/params')
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Нет параметров', html)


class HeadersPageTests(unittest.TestCase):
    """Заголовки запроса — имена и значения."""

    def test_headers_page_lists_custom_header_name_and_value(self):
        with app.test_client() as c:
            rv = c.get('/headers', headers={'X-Lab-Test': 'alpha-beta'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('X-Lab-Test', html)
            self.assertIn('alpha-beta', html)

    def test_headers_page_includes_host_header(self):
        with app.test_client() as c:
            rv = c.get('/headers')
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Host', html)


class CookiePageTests(unittest.TestCase):
    """Cookie — установка при отсутствии и удаление при наличии."""

    def test_cookie_sets_demo_cookie_when_not_present(self):
        with app.test_client() as c:
            rv = c.get('/cookie')
            self.assertEqual(rv.status_code, 200)
            set_cookies = rv.headers.getlist('Set-Cookie')
            self.assertTrue(
                any(DEMO_COOKIE_NAME in part for part in set_cookies),
                'Ожидается Set-Cookie с именем демо-куки',
            )
            body = rv.data.decode('utf-8')
            self.assertIn(DEMO_COOKIE_VALUE, body)
            self.assertIn('установлен', body.lower())

    def test_cookie_deletes_demo_cookie_when_already_set(self):
        with app.test_client() as c:
            c.get('/cookie')
            rv = c.get('/cookie')
            self.assertEqual(rv.status_code, 200)
            body = rv.data.decode('utf-8')
            self.assertIn('удален', body.lower())


class FormPageTests(unittest.TestCase):
    """Параметры формы после POST."""

    def test_form_post_displays_submitted_field_values(self):
        with app.test_client() as c:
            rv = c.post(
                '/form',
                data={'name': 'Иван', 'age': '21'},
                follow_redirects=True,
            )
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Иван', html)
            self.assertIn('21', html)
            self.assertIn('name', html)
            self.assertIn('age', html)


class PhoneValidationTests(unittest.TestCase):
    """Валидация и форматирование телефона, Bootstrap-классы."""

    def test_check_phone_get_renders_form_without_error(self):
        with app.test_client() as c:
            rv = c.get('/check_phone')
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertNotIn('is-invalid', html)
            self.assertNotIn(ERR_PHONE_DIGITS, html)

    def test_phone_valid_plus7_parentheses_format(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '+7 (123) 456-75-90'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('8-123-456-75-90', html)
            self.assertNotIn('is-invalid', html)

    def test_phone_valid_8_without_spaces(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '8(123)4567590'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('8-123-456-75-90', html)

    def test_phone_valid_ten_digits_with_dots(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '123.456.75.90'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('8-123-456-75-90', html)

    def test_phone_invalid_characters_shows_chars_error_and_bootstrap(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '12a34'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(ERR_PHONE_CHARS, html)
            self.assertIn('is-invalid', html)
            self.assertIn('invalid-feedback', html)

    def test_phone_invalid_digit_count_shows_digits_error_and_bootstrap(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '12345'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(ERR_PHONE_DIGITS, html)
            self.assertIn('is-invalid', html)
            self.assertIn('invalid-feedback', html)

    def test_phone_eleven_digit_start_8_wrong_count_shows_digits_error(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '8123456789'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(ERR_PHONE_DIGITS, html)

    def test_phone_empty_input_shows_digit_error(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': ''})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(ERR_PHONE_DIGITS, html)
            self.assertIn('is-invalid', html)

    def test_phone_forbidden_symbol_underscore_chars_error(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '+7_1234567890'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn(ERR_PHONE_CHARS, html)

    def test_successful_phone_no_invalid_feedback_block_for_error_text(self):
        with app.test_client() as c:
            rv = c.post('/check_phone', data={'phone': '+7 912 345 67 89'})
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('8-912-345-67-89', html)
            self.assertNotIn(ERR_PHONE_DIGITS, html)
            self.assertNotIn(ERR_PHONE_CHARS, html)


if __name__ == '__main__':
    unittest.main()
