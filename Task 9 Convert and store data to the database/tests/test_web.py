from myapp import *
from functools import wraps
import unittest

MODELS = (BaseModel, Driver)


def use_test_db(method):
    @wraps(method)
    def inner(self):
        test_db = SqliteDatabase(':memory:')
        with test_db.bind_ctx(MODELS):
            test_db.create_tables(MODELS)
            try:
                method(self)
            finally:
                test_db.drop_tables(MODELS)
    return inner


class TestWeb(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    @use_test_db
    def test_report_form(self):
        data = [
            {'id': 'LHM', 'name': 'Lewis Hamilton', 'car': 'MERCEDES', 'start_time': '12:18:20.125',
             'end_time': '1:11:32.585', 'delta_time': '0:53:12.460000'},
            {'id': 'SSW', 'name': 'Sergey Sirotkin', 'car': 'WILLIAMS MERCEDES', 'start_time': '12:16:11.648',
             'end_time': '1:11:24.354', 'delta_time': '0:55:12.706000'},
            {'id': 'EOF', 'name': 'Esteban Ocon', 'car': 'FORCE INDIA MERCEDES', 'start_time': '12:17:58.810',
             'end_time': '1:12:11.838', 'delta_time': '0:54:13.028000'}
            ]
        fields = [Driver.id, Driver.name, Driver.car, Driver.start_time, Driver.end_time, Driver.delta_time]
        Driver.insert_many(data, fields).execute()

        response = self.client.get("/report")
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'SSW', response.data)
            self.assertNotIn(b'Sergio Perez', response.data)
            self.assertIn(b'MERCEDES', response.data)
            self.assertIn(b'12:18:20.125', response.data)
            self.assertIn(b'1:11:24.354', response.data)
            self.assertIn(b'0:55:12.706000', response.data)

    @use_test_db
    def test_show_report(self):
        data = [
            {'id': 'LHM', 'name': 'Lewis Hamilton', 'car': 'MERCEDES', 'start_time': '12:18:20.125',
             'end_time': '1:11:32.585', 'delta_time': '0:53:12.460000'},
            {'id': 'SSW', 'name': 'Sergey Sirotkin', 'car': 'WILLIAMS MERCEDES', 'start_time': '12:16:11.648',
             'end_time': '1:11:24.354', 'delta_time': '0:55:12.706000'},
            {'id': 'EOF', 'name': 'Esteban Ocon', 'car': 'FORCE INDIA MERCEDES', 'start_time': '12:17:58.810',
             'end_time': '1:12:11.838', 'delta_time': '0:54:13.028000'}
        ]
        fields = [Driver.id, Driver.name, Driver.car, Driver.start_time, Driver.end_time, Driver.delta_time]
        Driver.insert_many(data, fields).execute()

        response = self.client.get("/report/?order=desc")
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'MES', response.data)
            self.assertNotIn(b'Pierre Gasly', response.data)
            self.assertIn(b'WILLIAMS MERCEDES', response.data)
            self.assertIn(b'12:16:11.648', response.data)
            self.assertIn(b'1:11:24.354', response.data)
            self.assertIn(b'0:53:12.460000', response.data)

    @use_test_db
    def test_drivers_form(self):
        data = [
            {'id': 'LHM', 'name': 'Lewis Hamilton', 'car': 'MERCEDES', 'start_time': '12:18:20.125',
             'end_time': '1:11:32.585', 'delta_time': '0:53:12.460000'},
            {'id': 'SSW', 'name': 'Sergey Sirotkin', 'car': 'WILLIAMS MERCEDES', 'start_time': '12:16:11.648',
             'end_time': '1:11:24.354', 'delta_time': '0:55:12.706000'},
            {'id': 'EOF', 'name': 'Esteban Ocon', 'car': 'FORCE INDIA MERCEDES', 'start_time': '12:17:58.810',
             'end_time': '1:12:11.838', 'delta_time': '0:54:13.028000'}
        ]
        fields = [Driver.id, Driver.name, Driver.car, Driver.start_time, Driver.end_time, Driver.delta_time]
        Driver.insert_many(data, fields).execute()

        response = self.client.get("/report/drivers")
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'EOF', response.data)
            self.assertIn(b'Sergey Sirotkin', response.data)
            self.assertNotIn(b'FORCE INDIA MERCEDES', response.data)
            self.assertNotIn(b'12:18:20.125', response.data)
            self.assertNotIn(b'1:11:32.585', response.data)
            self.assertNotIn(b'0:54:13.028000', response.data)

    @use_test_db
    def test_drivers_report_ordered(self):
        data = [
            {'id': 'LHM', 'name': 'Lewis Hamilton', 'car': 'MERCEDES', 'start_time': '12:18:20.125',
             'end_time': '1:11:32.585', 'delta_time': '0:53:12.460000'},
            {'id': 'SSW', 'name': 'Sergey Sirotkin', 'car': 'WILLIAMS MERCEDES', 'start_time': '12:16:11.648',
             'end_time': '1:11:24.354', 'delta_time': '0:55:12.706000'},
            {'id': 'EOF', 'name': 'Esteban Ocon', 'car': 'FORCE INDIA MERCEDES', 'start_time': '12:17:58.810',
             'end_time': '1:12:11.838', 'delta_time': '0:54:13.028000'}
        ]
        fields = [Driver.id, Driver.name, Driver.car, Driver.start_time, Driver.end_time, Driver.delta_time]
        Driver.insert_many(data, fields).execute()

        response = self.client.get("/report/drivers/?order=desc")
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'LHM', response.data)
            self.assertIn(b'Esteban Ocon', response.data)
            self.assertNotIn(b'MERCEDES', response.data)
            self.assertNotIn(b'12:18:20.125', response.data)
            self.assertNotIn(b'1:11:32.585', response.data)
            self.assertNotIn(b'0:54:13.028000', response.data)

    @use_test_db
    def test_drivers_report_single_driver(self):
        data = [
            {'id': 'LHM', 'name': 'Lewis Hamilton', 'car': 'MERCEDES', 'start_time': '12:18:20.125',
             'end_time': '1:11:32.585', 'delta_time': '0:53:12.460000'},
            {'id': 'SSW', 'name': 'Sergey Sirotkin', 'car': 'WILLIAMS MERCEDES', 'start_time': '12:16:11.648',
             'end_time': '1:11:24.354', 'delta_time': '0:55:12.706000'},
            {'id': 'EOF', 'name': 'Esteban Ocon', 'car': 'FORCE INDIA MERCEDES', 'start_time': '12:17:58.810',
             'end_time': '1:12:11.838', 'delta_time': '0:54:13.028000'}
        ]
        fields = [Driver.id, Driver.name, Driver.car, Driver.start_time, Driver.end_time, Driver.delta_time]
        Driver.insert_many(data, fields).execute()

        response = self.client.get("/report/drivers/?driver_id=LHM")
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'LHM', response.data)
            self.assertIn(b'Lewis Hamilton', response.data)
            self.assertIn(b'MERCEDES', response.data)
            self.assertIn(b'12:18:20.125', response.data)
            self.assertIn(b'1:11:32.585', response.data)
            self.assertNotIn(b'0:55:12.706000', response.data)

    def tearDown(self):
        self.client = None


if __name__ == "__main__":
    unittest.main()

