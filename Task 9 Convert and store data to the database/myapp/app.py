from myapp.create_tables import *
from flask import Flask, render_template, request, make_response
from flask_restful import Resource, Api, abort

from playhouse.shortcuts import model_to_dict
from dicttoxml import dicttoxml
import itertools
import json


app = Flask(__name__, template_folder="../templates", static_folder="../static")
api = Api(app)


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route("/report")
def report_form():
    result = (Driver
              .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                      Driver.end_time, Driver.delta_time)
              .order_by(Driver.delta_time.asc()))

    return render_template("report_form.html", the_result=result)


class CommonStatistic(Resource):
    def build_api_common_statistic(self):
        report = (Driver
                  .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                          Driver.end_time, Driver.delta_time)
                  .order_by(Driver.delta_time.asc()))

        converted_to_dict_report = []
        for driver_obj in report:
            driver_dict = model_to_dict(driver_obj)
            converted_to_dict_report.append(driver_dict)

        return {"total": len(report), "title": "Monaco Racing 2018", "drivers": converted_to_dict_report}

    def get(self):
        report_format = request.args.get("format")
        if report_format == "json":
            return self.build_api_common_statistic()
        elif report_format == "xml":
            report = self.build_api_common_statistic()
            drivers_item_func = lambda x: "driver"
            xml = dicttoxml(report, attr_type=False, custom_root="full_report", item_func=drivers_item_func)
            response = make_response(xml)
            response.headers["Content-Type"] = "application/xml"
            return response
        else:
            abort(404)


@app.route("/report/", methods=["GET"])
def show_report():
    order = request.args.get("order")
    if order == "asc":
        result = (Driver
                  .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                          Driver.end_time, Driver.delta_time)
                  .order_by(Driver.delta_time.asc()))

        return render_template("show_report.html", the_order=order, the_result=result)

    elif order == "desc":
        result = (Driver
                  .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                          Driver.end_time, Driver.delta_time)
                  .order_by(Driver.delta_time.desc()))

        return render_template("show_report.html", the_order=order, the_result=result)


class OrderedCommonStatistic(Resource):
    def build_api_ordered_common_statistic(self):
        order = request.args.get("order")
        if order == "asc":
            report = (Driver
                      .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                              Driver.end_time, Driver.delta_time)
                      .order_by(Driver.delta_time.asc()))

            converted_to_dict_report = []
            for driver_obj in report:
                driver_dict = model_to_dict(driver_obj, recurse=False)
                converted_to_dict_report.append(driver_dict)

            return {"total": len(report), "title": "Monaco Racing 2018", "drivers": converted_to_dict_report}

        elif order == "desc":
            report = (Driver
                      .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                              Driver.end_time, Driver.delta_time)
                      .order_by(Driver.delta_time.desc()))

            converted_to_dict_report = []
            for driver_obj in report:
                driver_dict = model_to_dict(driver_obj, recurse=False)
                converted_to_dict_report.append(driver_dict)

            return {"total": len(report), "title": "Monaco Racing 2018", "drivers": converted_to_dict_report}

    def get(self):
        report_format = request.args.get("format")
        if report_format == "json":
            return self.build_api_ordered_common_statistic()
        elif report_format == "xml":
            report = self.build_api_ordered_common_statistic()
            drivers_item_func = lambda x: "driver"
            xml = dicttoxml(report, attr_type=False, custom_root="full_report", item_func=drivers_item_func)
            response = make_response(xml)
            response.headers["Content-Type"] = "application/xml"
            return response
        else:
            abort(404)


@app.route("/report/drivers")
def drivers_form():
    result = (Driver
              .select(Driver.id, Driver.name)
              .order_by(Driver.delta_time.asc()))

    return render_template("drivers_form.html", the_result=result)


class DriversNames(Resource):
    def build_api_drivers_names(self):
        report = (Driver
                  .select(Driver.id, Driver.name)
                  .order_by(Driver.delta_time.asc()))

        converted_to_dict_report = []
        for driver_obj in report:
            driver_dict = model_to_dict(driver_obj, recurse=False)
            converted_to_dict_report.append(driver_dict)

        data = []
        for driver in converted_to_dict_report:
            driver_shorten = dict(itertools.islice(driver.items(), 2))
            driver_converted = json.loads(json.dumps(driver_shorten))
            data.append(driver_converted)

        return {"total": len(report), "title": "Monaco Racing 2018 Drivers", "drivers": data}

    def get(self):
        report_format = request.args.get("format")
        if report_format == "json":
            return self.build_api_drivers_names()
        elif report_format == "xml":
            report = self.build_api_drivers_names()
            drivers_item_func = lambda x: "driver"
            xml = dicttoxml(report, attr_type=False, custom_root="full_report", item_func=drivers_item_func)
            response = make_response(xml)
            response.headers["Content-Type"] = "application/xml"
            return response
        else:
            abort(404)


@app.route("/report/drivers/")
def drivers_report():
    order = request.args.get("order")
    if "order" in request.args:
        if order == "asc":

            result = (Driver
                      .select(Driver.id, Driver.name)
                      .order_by(Driver.delta_time.asc()))

            return render_template("drivers_report.html", the_order=order, the_result=result)

        elif order == "desc":
            result = (Driver
                      .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                              Driver.end_time, Driver.delta_time)
                      .order_by(Driver.delta_time.desc()))

            return render_template("drivers_report.html", the_order=order, the_result=result)

    elif "driver_id" in request.args:
        driver_id = request.args.get("driver_id")
        result = (Driver
                  .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                          Driver.end_time, Driver.delta_time)
                  .where(Driver.id == driver_id))

        return render_template("driver_info.html", the_result=result)


class OrderedDriversNames(Resource):
    def build_api_ordered_drivers_names(self):
        order = request.args.get("order")

        if order == "asc":
            report = (Driver
                      .select(Driver.id, Driver.name)
                      .order_by(Driver.delta_time.asc()))

            converted_to_dict_report = []
            for driver_obj in report:
                driver_dict = model_to_dict(driver_obj, recurse=False)
                converted_to_dict_report.append(driver_dict)

            data = []
            for driver in converted_to_dict_report:
                driver_shorten = dict(itertools.islice(driver.items(), 2))
                driver_converted = json.loads(json.dumps(driver_shorten))
                data.append(driver_converted)

            return {"total": len(report), "title": "Monaco Racing 2018 Drivers", "drivers": data}

        elif order == "desc":
            report = (Driver
                      .select(Driver.id, Driver.name)
                      .order_by(Driver.delta_time.desc()))

            converted_to_dict_report = []
            for driver_obj in report:
                driver_dict = model_to_dict(driver_obj, recurse=False)
                converted_to_dict_report.append(driver_dict)

            data = []
            for driver in converted_to_dict_report:
                driver_shorten = dict(itertools.islice(driver.items(), 2))
                driver_converted = json.loads(json.dumps(driver_shorten))
                data.append(driver_converted)

            return {"total": len(report), "title": "Monaco Racing 2018 Drivers", "drivers": data}

    def get(self):
        report_format = request.args.get("format")
        if report_format == "json":
            return self.build_api_ordered_drivers_names()
        elif report_format == "xml":
            report = self.build_api_ordered_drivers_names()
            drivers_item_func = lambda x: "driver"
            xml = dicttoxml(report, attr_type=False, custom_root="full_report", item_func=drivers_item_func)
            response = make_response(xml)
            response.headers["Content-Type"] = "application/xml"
            return response
        else:
            abort(404)


class SingleDriver(Resource):
    def build_api_driver(self):
        driver_id = request.args.get("driver_id")
        report = (Driver
                  .select(Driver.id, Driver.name, Driver.car, Driver.start_time,
                          Driver.end_time, Driver.delta_time)
                  .where(Driver.id == driver_id))

        converted_to_dict_report = []
        for driver_obj in report:
            driver_dict = model_to_dict(driver_obj, recurse=False)
            converted_to_dict_report.append(driver_dict)

        return {"total": len(report), "title": "Monaco Racing 2018 Driver Information",
                "drivers": converted_to_dict_report}

    def get(self):
        report_format = request.args.get("format")
        if report_format == "json":
            return self.build_api_driver()
        elif report_format == "xml":
            report = self.build_api_driver()
            drivers_item_func = lambda x: "driver"
            xml = dicttoxml(report, attr_type=False, custom_root="full_report", item_func=drivers_item_func)
            response = make_response(xml)
            response.headers["Content-Type"] = "application/xml"
            return response
        else:
            abort(404)


api.add_resource(CommonStatistic, "/api/v1.0/report")
api.add_resource(OrderedCommonStatistic, "/api/v1.0/report/")
api.add_resource(DriversNames, "/api/v1.0/report/drivers")
api.add_resource(OrderedDriversNames, "/api/v1.0/report/drivers/ordered")
api.add_resource(SingleDriver, "/api/v1.0/report/drivers/driver")


if __name__ == "__main__":
    app.run(debug=True)
