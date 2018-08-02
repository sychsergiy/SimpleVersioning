import json
import requests

from typing import Union

from griphook.api.graphite.target import DotPath
from griphook.server.average_load.graphite import average, summarize
from griphook.server.models import ServicesGroup, Service


def construct_target(metric_type, server='*', services_group='*', service='*', instance='*'):
    path = DotPath('cantal', '*', f'{server}', 'cgroups', 'lithos', f'{services_group}:{service}', f'{instance}')
    return str(path + metric_type)


def send_request(target: Union[str, tuple], time_from: int, time_until: int) -> dict:
    """
    Helper function for sending requests to Graphite APi
    :param target: Graphite API `target` argument
    :param time_from: timestamp
    :param time_until: timestamp
    :return: already parsed to json response
    """
    base_url = 'https://graphite.olympus.evo/render'
    params = {
        'format': 'json',
        'target': target,
        'from': str(time_from),
        'until': str(time_until),
    }
    # todo: handle connection exception
    response = requests.get(url=base_url, params=params or {}, verify=False)
    return json.loads(response.text)


# todo: find better name for this class
class ChartDataHelper(object):
    """
    Helper class for average services load endpoints.
    Provide convenient interface to work with services
     hierarchy(cluster, server, service_group, service, instance)
    Flexible interface for constructing `target` argument for each item in hierarchy
    """

    def __init__(self, root: str, metric_type: str):
        self.root: str = root
        self.metric_type: str = metric_type
        self.children: tuple = self.retrieve_children()

    def retrieve_children(self) -> tuple:
        """
        Retrieve children instances for root:
         servers for cluster
         services groups for server
         services for services group

        Basically this method makes db query and returns tuple of children_items,
        format of children_item format is arbitrary, but keep in mind that
        `children_target_constructor` method retrieves it as argument

        :return: tuple[any], mostly tuple[str], tuple[tuple[str]] for services
        """
        # todo graphite avg function can't receive empty list
        raise NotImplementedError

    def children_target_constructor(self, children_item) -> str:
        """
        Each inherited item in hierarchy(cluster, server, service_group, service)
         has it own logic of constructing `target` argument for Graphite api, implement it here.
        :param children_item: item from collection returned by `retrieve_children` method, keep in mind!
        :return: path to objects to be obtained from API
        """
        raise NotImplementedError

    def root_target_constructor(self) -> str:
        """
        Each inherited item in hierarchy(cluster, server, service_group, service)
         has it own logic of constructing `target` argument for Graphite api, implement it here.
        :return:
        """
        raise NotImplementedError

    def root_target(self):
        target = self.root_target_constructor()
        return average(summarize(target, "3month", "avg"))

    def children_target(self) -> str:
        """
        Generator for creating complex(multiple) `target` argument for Graphite API
         converted into Graphite average and summarize functions
        :return: constructed target for one children_item:
            avg(summarize(cantal.*.*.cgroups.lithos.adv-stable:adv-ua.*.vsize,"3month","avg",false))
        """
        for item in self.children:
            target = self.children_target_constructor(item)
            yield average(summarize(target, "3month", 'avg'))

    def get_data(self, time_from: int, time_until: int) -> dict:
        """
        Function sending request to Graphite API and
         converting response to convenient format
        :param time_from: timestamp
        :param time_until: timestamp
        :return:
        """
        # target to root
        root_target = self.root_target()
        # target without wraps of avg and summarize functions
        # more user friendly format for showing on hover in chart
        root_target_to_visualize = self.root_target_constructor()

        # send request to Graphite API with root target
        parent_response = send_request(root_target, time_from, time_until)

        # parse json
        root_response_value = parent_response[0]['datapoints'][0][0]

        root_data = {'target': root_target_to_visualize, 'value': root_response_value}

        # tuple of targets(item is target for each children_item) for sending multiple target argument
        children_target = tuple(self.children_target())
        # send request to Graphite API with root target
        children_response = send_request(children_target, time_from, time_until)
        # convert response to convenient form
        children_data = [{
            'target': self.children_target_constructor(self.children[index]),
            'values': value['datapoints'][0][0],  # todo: check IndexError
        } for index, value in enumerate(children_response)]

        result = {
            'root': root_data,
            'children': children_data
        }
        return result


class ServerChartDataHelper(ChartDataHelper):
    def retrieve_children(self) -> tuple:
        services_groups = (
            Service.query
                .filter(Service.server == self.root)
                .join(ServicesGroup).distinct()
                .with_entities(ServicesGroup.title)
        ).all()
        return tuple(services_group_title for (services_group_title,) in services_groups)

    def children_target_constructor(self, children_item) -> str:
        # get average value for each service_group inside this server
        # as service_group can be in few server, calculate only using instances from current server
        # be careful, when you watch average on service_group detail it will be not the same
        return construct_target(self.metric_type, server=self.root, services_group=children_item)

    def root_target_constructor(self) -> str:
        return construct_target(self.metric_type, server=self.root)


class ServicesGroupChartDataHelper(ChartDataHelper):
    def retrieve_children(self) -> tuple:
        services = (
            ServicesGroup.query
                .filter(ServicesGroup.title == self.root)
                .join(Service).distinct()
                .with_entities(Service.title)
        ).all()

        # convert to simple structure without nesting
        services = tuple(title for (title,) in services)
        return services

    def children_target_constructor(self, children_item) -> str:
        return construct_target(self.metric_type, services_group=self.root, service=children_item)

    def root_target_constructor(self) -> str:
        return construct_target(self.metric_type, services_group=self.root)


class ServicesChartDataHelper(ChartDataHelper):
    def retrieve_children(self) -> tuple:
        services = (
            Service.query
                .filter(Service.title == self.root).distinct()
                .join(ServicesGroup)
                .with_entities(Service.server, ServicesGroup.title, Service.title, Service.instance, )
        ).all()
        # necessary to use full path for services
        # because services may have the same name, but relate to different servers
        return services

    def children_target_constructor(self, children_item) -> str:
        # use format in accordance to `retrieve_children` method returns
        server, group, service, instance = children_item
        return construct_target(self.metric_type, server=server, services_group=group, service=service,
                                instance=instance)

    def root_target_constructor(self) -> str:
        return construct_target(self.metric_type, service=self.root)
