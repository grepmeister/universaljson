#!/usr/bin/env python3

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    SimpleLevels,
    List,
    String,
    InputHint,
    LevelsType,
    validators,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form():
    return Dictionary(
        elements={
            "hosts_up_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Lower percentage threshold for host in UP status"),
                    form_spec_template=Float(),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue(value=(90.0, 80.0)),
                ),
                required=True,
            ),
            "services_ok_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Lower percentage threshold for services in OK status"),
                    form_spec_template=Float(),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue(value=(90.0, 80.0)),
                ),
                required=True,
            ),
        }
    )


def _my_parameter_form_dict():
    return Dictionary(
        title=Title("Service Metric Configuration"),  # Or another title as needed
        elements={
            "metrics_thresholds": DictElement(
                parameter_form=_my_parameter_form_list(),
            )
        },
    )


def _my_parameter_form_list():
    return List(
        title=Title("Metrics thresholds"),
        add_element_label=Label("Add threshold for a metric"),
        # remove_element_label=Label("Remove this metric threshold"),
        # no_element_label=Label("Please add at least one metric"),
        element_template=Dictionary(
            elements={
                "metric": DictElement(
                    parameter_form=Dictionary(
                        title=Title("Metric thresholds"),
                        elements={
                            "name": DictElement(
                                parameter_form=String(
                                    title=Title("Name"),
                                    help_text=Help("The name of the metric"),
                                    prefill=InputHint("temp"),
                                ),
                                required=True,
                                # group=DictGroup(),
                            ),
                            "upper": DictElement(
                                parameter_form=SimpleLevels(
                                    title=Title("Upper levels"),
                                    form_spec_template=Float(),
                                    level_direction=LevelDirection.UPPER,
                                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                                    prefill_fixed_levels=InputHint((0.0, 0.0)),
                                ),
                                required=True,
                            ),
                            "lower": DictElement(
                                parameter_form=SimpleLevels(
                                    title=Title("Lower levels"),
                                    form_spec_template=Float(),
                                    level_direction=LevelDirection.LOWER,
                                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                                    prefill_fixed_levels=InputHint((0.0, 0.0)),
                                ),
                                required=True,
                            ),
                        },
                    ),
                    required=True,
                ),
            },
        ),
    )


rule_spec_myhostgroups = CheckParameters(
    name="universaljson",
    title=Title("UniversalJSON"),
    topic=Topic.GENERAL,
    parameter_form=_my_parameter_form_dict,
    condition=HostAndItemCondition(item_title=Title("Service item")),
)
