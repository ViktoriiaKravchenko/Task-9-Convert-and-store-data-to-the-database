from myapp import *
from functools import wraps
import unittest
from playhouse.test_utils import count_queries

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


class TestModels(unittest.TestCase):
    @use_test_db
    def test_insert_into_driver_table(self):
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

        expected = [
            ('LHM', 'Lewis Hamilton', 'MERCEDES', '12:18:20.125', '1:11:32.585', '0:53:12.460000'),
            ('EOF', 'Esteban Ocon', 'FORCE INDIA MERCEDES', '12:17:58.810', '1:12:11.838', '0:54:13.028000'),
            ('SSW', 'Sergey Sirotkin', 'WILLIAMS MERCEDES', '12:16:11.648', '1:11:24.354', '0:55:12.706000')]

        ordered_drivers_query = Driver.select().order_by(Driver.delta_time)
        actual = [(d.id, d.name, d.car, d.start_time, d.end_time, d.delta_time) for d in ordered_drivers_query]

        drivers_cars_query = Driver.select(Driver.car)
        drivers_cars = [driver.car for driver in drivers_cars_query]

        with self.subTest():
            self.assertEqual(actual, expected)
            self.assertEqual(drivers_cars, ["MERCEDES", "WILLIAMS MERCEDES", "FORCE INDIA MERCEDES"])
            self.assertEqual(Driver.select().count(), 3)
            with count_queries() as counter:
                driver_name = Driver.get(Driver.name == "Esteban Ocon")
            self.assertEqual(counter.count, 1)


if __name__ == "__main__":
    unittest.main()



