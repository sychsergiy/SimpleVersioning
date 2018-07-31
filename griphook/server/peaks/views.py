import datetime
import json
import pytz

from flask import current_app, request, abort
from sqlalchemy import func

from griphook.server.models import Metric, BatchStory, Service, ServicesGroup
from griphook.server.peaks.utils import round_time


def get_peacks():
    try:
        step = int(request.args.get('step'))
        since = datetime.datetime.strptime(request.args.get('since'), '%Y-%m-%d')
        until = datetime.datetime.strptime(request.args.get('until'), '%Y-%m-%d')
        service_group = request.args.get('services_group')
        service = request.args.get('service')
    except ValueError:
        abort(400)

    metric_type = request.args.get('metric_type')
    server = request.args.get('server')
    if not metric_type or not server:
        abort(400)

    until = round_time(since, until, step=step)
    since_timestamp = since.replace(tzinfo=datetime.timezone.utc).timestamp()
    remainder = (since_timestamp % step)
    group_time = (func.floor((func.extract('epoch', BatchStory.time) - remainder) / step)) * step
    query = (
        Metric.query
            .with_entities(
                func.max(Metric.value).label("peaks"),
                func.min(func.extract('epoch', BatchStory.time)),
                group_time.label('step')
        )
            .group_by('step')
            .order_by('step')
            .join(BatchStory)
            .join(Service)
            .join(ServicesGroup)
            .filter(BatchStory.time.between(since, until))
            .filter(Metric.type==metric_type)
        )
    if server:
        query = query.filter(Service.server==server)
        if service_group:
            query = query.filter(ServicesGroup.title==service_group)
            if service:
                query = query.filter(Service.title)

    formatter = lambda x : (
                x[0],
                datetime.datetime.fromtimestamp(
                    x[1],
                    tz=pytz.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
    )
    data = [formatter(element) for element in query.all()]
    response_data = {'data': data}
    response = current_app.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json'
    )
    return response