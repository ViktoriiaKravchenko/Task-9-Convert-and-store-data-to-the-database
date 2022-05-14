from myapp import *
from functools import wraps
import unittest
import xml.etree.ElementTree as ET

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
    def test_build_api_common_statistic_json(self):
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

        response = self.client.get("/api/v1.0/report", query_string={"format": "json"})

        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertIn(b'"total": 3', response.data)
            self.assertIn(b'"title": "Monaco Racing 2018"', response.data)

            self.assertEqual(response.json["drivers"][1],
                             {
                                 "id": "EOF",
                                 "name": "Esteban Ocon",
                                 "car": "FORCE INDIA MERCEDES",
                                 "start_time": "12:17:58.810",
                                 "end_time": "1:12:11.838",
                                 "delta_time": "0:54:13.028000"
                             }
                             )

    @use_test_db
    def test_build_api_common_statistic_xml(self):
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

        response = self.client.get("/api/v1.0/report", query_string={"format": "xml"})

        root = ET.fromstring(response.data)

        for driver in root.findall("driver"):
            id = driver.findtext("id")
            name = driver.findtext("name")
            car = driver.findtext("car")
            start_time = driver.findtext("start_time")
            end_time = driver.findtext("end_time")
            delta_time = driver.findtext("delta_time")

            with self.subTest():
                self.assertEqual(id, "LHM")
                self.assertNotEqual(name, "Stoffel Vandoorne")
                self.assertEqual(car, "MERCEDES")
                self.assertEqual(start_time, "12:18:20.125")
                self.assertEqual(end_time, "1:11:32.585")
                self.assertEqual(delta_time, "0:53:12.460000")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")

    @use_test_db
    def test_build_api_common_statistic_error(self):
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

        response = self.client.get("/api/v1.0/report", query_string={"format": ""})

        self.assertEqual(response.status_code, 404)

    @use_test_db
    def test_build_api_ordered_common_statistic_json(self):
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

        response = self.client.get("/api/v1.0/report/", query_string={"order": "asc", "format": "json"})

        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertIn(b'"total": 3', response.data)
            self.assertIn(b'"title": "Monaco Racing 2018"', response.data)

            self.assertEqual(response.json["drivers"][0],
                             {
                                 "id": "LHM",
                                 "name": "Lewis Hamilton",
                                 "car": "MERCEDES",
                                 "start_time": "12:18:20.125",
                                 "end_time": "1:11:32.585",
                                 "delta_time": "0:53:12.460000"
                             }
                             )

    @use_test_db
    def test_build_api_ordered_common_statistic_xml(self):
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

        response = self.client.get("/api/v1.0/report/", query_string={"order": "desc", "format": "xml"})

        root = ET.fromstring(response.data)

        for driver in root.findall("driver"):
            id = driver.findtext("id")
            name = driver.findtext("name")
            car = driver.findtext("car")
            start_time = driver.findtext("start_time")
            end_time = driver.findtext("end_time")
            delta_time = driver.findtext("delta_time")

            with self.subTest():
                self.assertEqual(id, "SSW")
                self.assertEqual(name, "Sergey Sirotkin")
                self.assertEqual(car, "WILLIAMS MERCEDES")
                self.assertNotEqual(start_time, "12:18:20.125")
                self.assertEqual(end_time, "1:11:24.354")
                self.assertEqual(delta_time, "0:55:12.706000")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")

    @use_test_db
    def test_build_api_ordered_common_statistic_error(self):
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

        response = self.client.get("/api/v1.0/report/", query_string={"order": "desc", "format": ""})

        self.assertEqual(response.status_code, 404)

    @use_test_db
    def test_build_api_drivers_names_json(self):
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

        response = self.client.get("/api/v1.0/report/drivers", query_string={"format": "json"})

        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertIn(b'"total": 3', response.data)
            self.assertIn(b'"title": "Monaco Racing 2018 Drivers"', response.data)

            self.assertEqual(response.json["drivers"][2],
                             {
                                 "id": "SSW",
                                 "name": "Sergey Sirotkin"
                             })

    @use_test_db
    def test_build_api_drivers_names_xml(self):
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

        response = self.client.get("/api/v1.0/report/drivers", query_string={"format": "xml"})

        root = ET.fromstring(response.data)

        for driver in root.findall("driver"):
            id = driver.findtext("id")
            name = driver.findtext("name")

            with self.subTest():
                self.assertEqual(id, "LHM")
                self.assertNotEqual(name, "Esteban Ocon")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")

    @use_test_db
    def test_build_api_drivers_names_error(self):
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

        response = self.client.get("/api/v1.0/report/drivers", query_string={"format": ""})

        self.assertEqual(response.status_code, 404)

    @use_test_db
    def test_build_api_ordered_drivers_names_json(self):
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

        response = self.client.get("/api/v1.0/report/drivers/ordered", query_string={"order": "desc", "format": "json"})

        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertIn(b'"total": 3', response.data)
            self.assertIn(b'"title": "Monaco Racing 2018 Drivers"', response.data)

            self.assertEqual(response.json["drivers"][0],
                             {
                                 "id": "SSW",
                                 "name": "Sergey Sirotkin"
                             })

    @use_test_db
    def test_build_api_ordered_drivers_names_xml(self):
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

        response = self.client.get("/api/v1.0/report/drivers/ordered", query_string={"order": "asc", "format": "xml"})

        root = ET.fromstring(response.data)

        for driver in root.findall("driver"):
            id = driver.findtext("id")
            name = driver.findtext("name")

            with self.subTest():
                self.assertEqual(id, "LHM")
                self.assertEqual(name, "Lewis Hamilton")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")

    @use_test_db
    def test_build_api_ordered_drivers_names_error(self):
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

        response = self.client.get("/api/v1.0/report/drivers/ordered", query_string={"order": "asc", "format": ""})

        self.assertEqual(response.status_code, 404)

    @use_test_db
    def test_build_api_driver_json(self):
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

        response = self.client.get("/api/v1.0/report/drivers/driver", query_string={"driver_id": "EOF",
                                                                                    "format": "json"})
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertIn(b'"title": "Monaco Racing 2018 Driver Information"', response.data)

            self.assertEqual(response.json["drivers"][0],
                             {
                                 "id": "EOF",
                                 "name": "Esteban Ocon",
                                 "car": "FORCE INDIA MERCEDES",
                                 "start_time": "12:17:58.810",
                                 "end_time": "1:12:11.838",
                                 "delta_time": "0:54:13.028000"
                             }
                             )

    @use_test_db
    def test_build_api_driver_xml(self):
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

        response = self.client.get("/api/v1.0/report/drivers/driver", query_string={"driver_id": "SSW",
                                                                                    "format": "xml"})

        root = ET.fromstring(response.data)

        for driver in root.findall("driver"):
            id = driver.findtext("id")
            name = driver.findtext("name")
            car = driver.findtext("car")
            start_time = driver.findtext("start_time")
            end_time = driver.findtext("end_time")
            delta_time = driver.findtext("delta_time")

            with self.subTest():
                self.assertEqual(id, "SSW")
                self.assertEqual(name, "Sergey Sirotkin")
                self.assertEqual(car, "WILLIAMS MERCEDES")
                self.assertEqual(start_time, "12:16:11.648")
                self.assertEqual(end_time, "1:11:24.354")
                self.assertEqual(delta_time, "0:55:12.706000")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/xml")

    @use_test_db
    def test_build_api_driver_error(self):
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

        response = self.client.get("/api/v1.0/report/drivers/driver", query_string={"driver_id": "SSW", "format": ""})

        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.client = None


if __name__ == "__main__":
    unittest.main()
