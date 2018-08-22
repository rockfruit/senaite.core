# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.api import get_uid, get_object_by_uid
from bika.lims.browser.fields.uidreferencefield import get_backreferences


def get_calculation_dependencies_for(service):
    """Calculation dependencies of this service and the calculation of each
    dependent service (recursively).
    """

    def calc_dependencies_gen(service, collector=None):
        """Generator for recursive dependency resolution.
        """

        # maintain an internal dependency mapping
        if collector is None:
            collector = {}

        # Get the calculation of the service.
        # The calculation comes either from an assigned method or the user
        # has set a calculation manually (see content/analysisservice.py).
        calculation = service.getCalculation()

        # Stop iteration if there is no calculation
        if not calculation:
            raise StopIteration

        # The services used in this calculation.
        # These are the actual dependencies of the used formula.
        dep_services = calculation.getDependentServices()
        for dep_service in dep_services:

            dep_uid = get_uid(dep_service)
            if dep_uid not in collector:
                # remember the dependent service
                collector[dep_uid] = dep_service
                # yield the dependent service
                yield dep_service

            # recurse
            ddeps = calc_dependencies_gen(dep_service, collector=collector)
            for ddep_service in ddeps:
                yield ddep_service

    dependencies = {}
    for dep_service in calc_dependencies_gen(service):
        # Skip the initial (requested) service
        if dep_service == service:
            continue
        uid = get_uid(dep_service)
        dependencies[uid] = dep_service

    return dependencies


def get_calculation_dependants_for(service):
    """Calculation dependants of this service
    """

    def calc_dependants_gen(service, collector=None):
        """Generator for recursive resolution of dependant sevices.
        """

        # The UID of the service
        service_uid = get_uid(service)

        # maintain an internal dependency mapping
        if collector is None:
            collector = {}

        # Stop iteration if we processed this service already
        if service_uid in collector:
            raise StopIteration

        # Get the dependant calculations of the service
        # (calculations that use the service in their formula).
        c_refs = get_backreferences(service, 'CalculationDependentServices')
        dep_calcs = map(get_object_by_uid, c_refs)
        for dep_calc in dep_calcs:

            # Get the services that have this calculation linked
            s_refs = get_backreferences(dep_calc, 'AnalysisServiceCalculation')
            dep_services = map(get_object_by_uid, s_refs)
            for dep_service in dep_services:

                # remember the dependent service
                collector[get_uid(dep_service)] = dep_service

                # yield the dependent service
                yield dep_service

                # check the dependants of the dependant services
                for ddep_service in calc_dependants_gen(
                        dep_service, collector=collector):
                    yield ddep_service

    dependants = {}
    for dep_service in calc_dependants_gen(service):
        # Skip the initial (requested) service
        if dep_service == service:
            continue
        uid = get_uid(dep_service)
        dependants[uid] = dep_service

    return dependants
