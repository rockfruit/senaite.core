Calculations
============

Tests the general Calculation functionality in bika/lims/api/calculations

Running this test from the buildout directory:

.. code-block:: sh

    bin/test -t API_calculation


Test Setup
----------

Needed Imports:

.. code-block:: python

    >>> from bika.lims.api import create
    >>> from bika.lims.api.calculation import get_calculation_dependants_for
    >>> from bika.lims.api.calculation import get_calculation_dependencies_for


Functional Helpers:

.. code-block:: python

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)


Variables:

.. code-block:: python

    >>> portal = self.portal
    >>> request = self.request
    >>> bs = portal.bika_setup


Test user:

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

.. code-block:: python

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

Create supporting objects:

.. code-block:: python

    >>> ca1 = create(bs.bika_analysisservices, "AnalysisService", title="Calcium1", Keyword="CA1")
    >>> ca2 = create(bs.bika_analysisservices, "AnalysisService", title="Calcium2", Keyword="CA2")
    >>> cacalc = create(bs.bika_calculations, "Calculation", title="Calcium Calc", Formula="[CA1] + [CA2]")
    >>> ca = create(bs.bika_analysisservices, "AnalysisService", title="Calcium", Calculation=cacalc, Keyword="CA")
    >>> mg = create(bs.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="MG")
    >>> thcalc = create(bs.bika_calculations, "Calculation", title="Total Hardness", Formula="[CA] + [MG]")
    >>> thserv = create(bs.bika_analysisservices, "AnalysisService", title="Total Hardness via Calculation", Calculation=thcalc, Keyword="TH")

Calculation dependants/dependencies
-----------------------------------

.. code-block:: python

    >>> [x.getKeyword() for x in get_calculation_dependants_for(ca).values()]
    ['TH']
    >>> [x.getKeyword() for x in get_calculation_dependants_for(mg).values()]
    ['TH']
    >>> [x.getKeyword() for x in get_calculation_dependants_for(thserv).values()]
    []
    >>> sorted([x.getKeyword() for x in get_calculation_dependencies_for(ca).values()])
    ['CA1', 'CA2']
    >>> [x.getKeyword() for x in get_calculation_dependencies_for(mg).values()]
    []
    >>> sorted([x.getKeyword() for x in get_calculation_dependencies_for(thserv).values()])
    ['CA', 'CA1', 'CA2', 'MG']
