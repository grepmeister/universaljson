#!/usr/bin/env python3

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Service,
    Result,
    State,
    Metric,
    check_levels,
    get_rate,
    get_value_store,
    get_average,
    GetRateError,
)

from pprintpp import pprint as pp
import json
import time

# https://nagios-plugins.org/doc/guidelines.html#AEN200
# UOM: s, us, ms, %, B, KB, MB, TB, c
# 'label'=value[UOM];[warn];[crit];[min];[max]

def lookup_metric_threshold(metric, params):
    # check if params contain a dict with metrics_thresholds
    if metrics_thresholds := params.get("metrics_thresholds"):
        # for each entry check if there are upper and/or lower levels
        for entry in metrics_thresholds:
            if entry['metric']['name'] == metric:
                return({
                    "upper" : entry['metric'].get('upper'),
                    "lower" : entry['metric'].get('lower'),
                })
    else:
        return {}

# map integers to chekcmk State.<constant>
# because the agent data provides these integers
def num2state(state):
    mapping = {
        0: State.OK,
        1: State.WARN,
        2: State.CRIT,
        3: State.UNKNOWN,
    }
    return mapping[state]


def parse_universaljson(string_table):
    parsed = json.loads(string_table[0][0])
    return parsed


def discover_universaljson(section):
    for service in section["services"]:
        #yield Service(item=service, parameters={"discovered": "parameter"})
        yield Service(item=service)


def check_universaljson(item, params, section):

    # Idea: we also could calculate the check latency, if the agent data would containe a timestamp
    ts = time.strftime("%F %T", time.localtime())

    # handle if item disappears
    if item not in section["services"]:
        yield Result(
            state=State.UNKNOWN,
            summary=f"item {item} not found anymore. consider to re-discover the services of this host again.",
        )
        # does this return make sense?
        return None

    # pick one service item
    s = section["services"][item]

    # check if we got metrics for this service item
    if metrics := s.get("metrics"):

        # iterate over the metrics
        for metric, value in metrics.items():

            # UOM is "c" for counter if last char is a c
            if isinstance(value, str):
                if value[-1] == "c":
                    value = float(value[:-1])
                    # use value as rate
                    value_store = get_value_store()
                    now = time.time()
                    try:
                        value = get_rate(value_store, metric, now, value)
                    except GetRateError:
                        value = 0.0
                        pass  # this fails the first time, because my_store is empty.

            # lookup if we have configured thresholds for this metric of this service item
            levels = lookup_metric_threshold(metric, params)

            # unfortunateley check_level overwrites my summary and details :-(, or? can i yield my own?
            yield from check_levels(
                value,
                levels_upper=levels.get('upper'),
                levels_lower=levels.get('lower'),
                metric_name=metric,
                label=metric,
                notice_only=False,
            )

    # in any case we yield a Result to get our summary details
    summary = s.get("summary", f"no summary for {item}")
    details = s.get("details", f"no details for {item}")
    if num := s.get("state"):
        state = num2state(num)
    else:
        state = State.OK

    yield Result(state=state, summary=summary, details=details)

    return None


# http://localhost:8080/mysite/check_mk/plugin-api/cmk.agent_based/v2.html#cmk.agent_based.v2.AgentSection
agent_section_universaljson = AgentSection(
    name="universaljson",
    parse_function=parse_universaljson,
)

# http://localhost:8080/mysite/check_mk/plugin-api/cmk.agent_based/v2.html#cmk.agent_based.v2.CheckPlugin
check_plugin_universaljson = CheckPlugin(
    name="universaljson",
    service_name="%s",
    discovery_function=discover_universaljson,
    check_function=check_universaljson,
    check_default_parameters={},
    check_ruleset_name="universaljson",
)
