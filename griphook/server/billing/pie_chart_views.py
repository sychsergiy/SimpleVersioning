from flask import request, jsonify
from flask.views import View

from sqlalchemy import func, case

from griphook.server.models import (
    ServicesGroup,
    Service,
    MetricBilling,
    BatchStoryBilling,
    Cluster,
    Server,
    Team,
    Project,
)

from griphook.server.billing.validation import validators, schemas


def get_price_coefficients(time_from, time_until):
    time_coefficient = (time_until - time_from).days / 30

    memory_convert_coefficient = time_coefficient / (
        10 ** 9
    )  # need to multiply on memory price
    cpu_convert_coefficient = (
        time_coefficient / 100
    )  # need to multiply on cpu price
    return memory_convert_coefficient, cpu_convert_coefficient


def get_average_metric_sum_func_with_cases(cpu_price_coef, memory_price_coef):
    average_function = func.avg(
        case(
            [
                (
                    MetricBilling.type == "user_cpu_percent",
                    MetricBilling.value * cpu_price_coef * Cluster.cpu_price,
                ),
                (
                    MetricBilling.type == "vsize",
                    MetricBilling.value
                    * memory_price_coef
                    * Cluster.memory_price,
                ),
            ],
            else_=0,
        )
    )
    return average_function


class GetPieChartAbsoluteDataView(View):
    """
    request format:
      {
        "target_type": one_of(project, team, cluster, server, services_group, all),
        "target_ids": [int],
        "time_from": "Y-M-D"
        "metric_type": one_of(user_cpu_percent, vsize)
        "time_until": "Y-M-D"
      }
      response format:
      {
        "labels": ["selected", "other"],
        "values": [int, int],
      ]
    return metric sum of selected_part
     (services groups filters by request params)
      relatively to total metric sum
    """

    methods = ["POST"]

    def dispatch_request(self):
        request_data = request.get_json() or {}
        valid, error_message, formatted_json = validators.validate_request_json(
            schemas.PIE_CHART_ENDPOINT_SCHEMA, request_data
        )
        if not valid:
            response = jsonify(error_message)
            response.status_code = 400
            return response

        total_initial_query = Service.query
        total_metric_sum = self.get_query_metric_sum(
            total_initial_query, request_data
        )

        target_type = request_data["target_type"]
        target_ids = request_data["target_ids"]

        if target_type == "all":
            initial_query = total_initial_query
        elif target_type == "cluster":
            initial_query = (
                Cluster.query.filter(Cluster.id.in_(target_ids))
                .join(Server, Server.cluster_id == Cluster.id)
                .join(Service, Server.id == Service.server_id)
            )
        elif target_type == "server":
            initial_query = Server.query.filter(Server.id.in_(target_ids)).join(
                Service, Service.server_id == Server.id
            )
        elif target_type == "services_group":
            initial_query = ServicesGroup.query.filter(
                ServicesGroup.id.in_(target_ids)
            ).join(Service, Service.services_group_id == ServicesGroup.id)
        elif target_type == "team":
            initial_query = (
                Team.query.filter(Team.id.in_(target_ids))
                .join(ServicesGroup, ServicesGroup.team_id == Team.id)
                .join(Service, Service.services_group_id == ServicesGroup.id)
            )
        elif target_type == "project":
            initial_query = (
                Project.query.filter(Project.id.in_(target_ids))
                .join(ServicesGroup, ServicesGroup.team_id == Project.id)
                .join(Service, Service.services_group_id == ServicesGroup.id)
            )
        else:
            raise Exception("Problem with request data validation")

        selected_metric_sum = self.get_query_metric_sum(
            initial_query, request_data
        )
        # todo: move this part to frontend
        if selected_metric_sum:
            response_data = {
                "labels": ("selected", "other"),
                "values": (
                    # todo: solve problem with ceiling in big number
                    round(selected_metric_sum, 0),
                    round(total_metric_sum - selected_metric_sum, 0),
                ),
            }
        else:
            response_data = {"labels": [], "values": []}
        return jsonify(response_data)

    def get_query_metric_sum(self, initial_query, request_data):
        """
        :param initial_query: query before joining with
         MetricBillling table, must be joined with Service or ServicesGroup
        """
        metric_sum = (
            initial_query.join(
                MetricBilling, Service.id == MetricBilling.service_id
            )
            .join(BatchStoryBilling)
            .filter(MetricBilling.type == request_data["metric_type"])
            .filter(
                BatchStoryBilling.time.between(
                    request_data["time_from"], request_data["time_until"]
                )
            )
            .with_entities(func.sum(MetricBilling.value).label("metric_sum"))
        ).scalar()
        return metric_sum


class GetPieChartRelativeDataView(View):
    """
    request format:
      {
        "target_type": one_of(project, team, cluster, server, services_group, all),
        "target_ids": [int],
        "time_from": "Y-M-D",
        "time_until": "Y-M-D",
        "metric_type": one_of("user_cpu_percent", "vsize")
      }
      response format:
      {
        "labels": [str],
        "values": [int],
      ]
    :return list of services groups and their's metric sum
    services groups are filtered by request params
    """

    methods = ["POST"]

    def dispatch_request(self):
        request_data = request.get_json() or {}
        valid, error_message, formatted_json = validators.validate_request_json(
            schemas.PIE_CHART_ENDPOINT_SCHEMA, request_data
        )
        if not valid:
            response = jsonify(error_message)
            response.status_code = 400
            return response

        target_type = request_data["target_type"]
        target_ids = request_data["target_ids"]

        if target_type == "all":
            initial_query = ServicesGroup.query
        elif target_type == "cluster":
            initial_query = (
                Cluster.query.filter(Cluster.id.in_(target_ids))
                .join(Server, Server.cluster_id == Cluster.id)
                .join(Service, Service.server_id == Server.id)
                .join(
                    ServicesGroup, Service.services_group_id == ServicesGroup.id
                )
            )
        elif target_type == "server":
            initial_query = (
                Server.query.filter(Server.id.in_(target_ids))
                .join(Service, Service.server_id == Server.id)
                .join(
                    ServicesGroup, ServicesGroup.id == Service.services_group_id
                )
            )
        elif target_type == "services_group":
            initial_query = ServicesGroup.query.filter(
                ServicesGroup.id.in_(target_ids)
            )
        elif target_type == "project":
            initial_query = Project.query.filter(
                Project.id.in_(target_ids)
            ).join(ServicesGroup, Project.id == ServicesGroup.project_id)
        elif target_type == "team":
            initial_query = Team.query.filter(Team.id.in_(target_ids)).join(
                ServicesGroup, Team.id == ServicesGroup.team_id
            )
        else:
            raise Exception(
                "Problem with request data validation, wrong target type"
            )

        groups_metric_sum_values = self.get_metric_sum_for_each_group(
            initial_query, request_data
        )

        # todo: move this part to frontend
        if groups_metric_sum_values:
            labels, values = zip(*groups_metric_sum_values)
        else:
            labels, values = [], []

        response_data = {"labels": labels, "values": values}
        return jsonify(response_data)

    def get_metric_sum_for_each_group(self, initial_query, request_data):
        """
        :param initial_query: query of ServicesGroups
        :param request_data: filter params
        :return: metric sum for each services group in initial query
        """

        total = (
            initial_query.join(
                MetricBilling,
                MetricBilling.services_group_id == ServicesGroup.id,
            )
            .join(BatchStoryBilling)
            .filter(MetricBilling.type == request_data["metric_type"])
            .filter(
                BatchStoryBilling.time.between(
                    request_data["time_from"], request_data["time_until"]
                )
            )
            .group_by(ServicesGroup.title)
            .order_by(func.sum(MetricBilling.value).desc())
            .with_entities(
                ServicesGroup.title,
                func.sum(MetricBilling.value).label("metric_sum"),
            )
        ).all()
        return total
