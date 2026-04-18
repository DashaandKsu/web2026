# -*- coding: utf-8 -*-
"""
Тесты для лабораторной работы №3.
Запуск из корня проекта:
    python -m pytest tests/test_lab3.py -v
    python -m unittest discover -s tests -p "test_lab3.py" -v
"""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_APP_DIR = os.path.join(_ROOT, 'app')
sys.path.insert(0, _APP_DIR)

import app as flask_app_module  # noqa: E402

app = flask_app_module.app


def login(client, username='user', password='qwerty', remember=False):
    data = {'login': username, 'password': password}
    if remember:
        data['remember'] = 'on'
    return client.post('/login', data=data, follow_redirects=True)


class VisitCounterTests(unittest.TestCase):
    """Счётчик посещений работает на основе session."""

    def test_counter_increments_on_each_visit(self):
        with app.test_client() as c:
            rv1 = c.get('/counter')
            rv2 = c.get('/counter')
            html = rv2.data.decode('utf-8')
            self.assertEqual(rv1.status_code, 200)
            self.assertIn('2', html)

    def test_counter_starts_at_one_for_new_session(self):
        with app.test_client() as c:
            rv = c.get('/counter')
            html = rv.data.decode('utf-8')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('1', html)

    def test_counter_is_independent_per_session(self):
        with app.test_client() as c1:
            c1.get('/counter')
            c1.get('/counter')
        with app.test_client() as c2:
            rv = c2.get('/counter')
            html = rv.data.decode('utf-8')
            self.assertIn('1', html)


class LoginSuccessTests(unittest.TestCase):
    """Успешная аутентификация."""

    def test_valid_credentials_redirect_to_index(self):
        with app.test_client() as c:
            rv = login(c)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('/', rv.request.path)

    def test_valid_login_shows_success_flash_message(self):
        with app.test_client() as c:
            rv = login(c)
            html = rv.data.decode('utf-8')
            self.assertIn('успешно', html.lower())

    def test_after_login_navbar_shows_secret_page_link(self):
        with app.test_client() as c:
            login(c)
            rv = c.get('/')
            html = rv.data.decode('utf-8')
            self.assertIn('Секретная страница', html)

    def test_after_login_navbar_hides_login_link(self):
        with app.test_client() as c:
            login(c)
            rv = c.get('/')
            html = rv.data.decode('utf-8')
            self.assertNotIn('href="/login"', html)


class LoginFailureTests(unittest.TestCase):
    """Неудачная аутентификация."""

    def test_wrong_password_stays_on_login_page(self):
        with app.test_client() as c:
            rv = login(c, password='wrong')
            self.assertIn('login', rv.request.path)

    def test_wrong_credentials_show_error_flash_message(self):
        with app.test_client() as c:
            rv = login(c, password='wrong')
            html = rv.data.decode('utf-8')
            self.assertIn('Неверный логин или пароль', html)


class SecretPageTests(unittest.TestCase):
    """Доступ к секретной странице."""

    def test_authenticated_user_can_access_secret_page(self):
        with app.test_client() as c:
            login(c)
            rv = c.get('/secret_page')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Секретная страница', rv.data.decode('utf-8'))

    def test_anonymous_user_redirected_to_login(self):
        with app.test_client() as c:
            rv = c.get('/secret_page', follow_redirects=True)
            self.assertIn('login', rv.request.path)

    def test_anonymous_user_sees_auth_required_message(self):
        with app.test_client() as c:
            rv = c.get('/secret_page', follow_redirects=True)
            html = rv.data.decode('utf-8')
            self.assertIn('аутентификацию', html.lower())

    def test_after_auth_redirected_to_secret_page_automatically(self):
        with app.test_client() as c:
            c.get('/secret_page')
            rv = c.post(
                '/login',
                data={'login': 'user', 'password': 'qwerty', 'next': '/secret_page'},
                follow_redirects=True,
            )
            self.assertIn('secret_page', rv.request.path)


class RememberMeTests(unittest.TestCase):
    """Параметр «Запомнить меня»."""

    def test_remember_me_sets_remember_token_cookie(self):
        with app.test_client() as c:
            rv = c.post('/login', data={'login': 'user', 'password': 'qwerty', 'remember': 'on'})
            set_cookies = rv.headers.getlist('Set-Cookie')
            self.assertTrue(
                any('remember_token' in part for part in set_cookies),
                'Ожидается Set-Cookie с remember_token при «Запомнить меня»',
            )

    def test_without_remember_me_no_remember_token_cookie(self):
        with app.test_client() as c:
            rv = c.post('/login', data={'login': 'user', 'password': 'qwerty'})
            set_cookies = rv.headers.getlist('Set-Cookie')
            self.assertFalse(
                any('remember_token' in part for part in set_cookies),
                'Cookie remember_token не должна устанавливаться без чекбокса',
            )


class NavbarVisibilityTests(unittest.TestCase):
    """Навбар корректно показывает/скрывает ссылки."""

    def test_anonymous_navbar_shows_login_link(self):
        with app.test_client() as c:
            rv = c.get('/')
            html = rv.data.decode('utf-8')
            self.assertIn('Вход', html)

    def test_anonymous_navbar_hides_secret_page_link(self):
        with app.test_client() as c:
            rv = c.get('/')
            html = rv.data.decode('utf-8')
            self.assertNotIn('Секретная страница', html)


if __name__ == '__main__':
    unittest.main()
