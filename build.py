#   -*- coding: utf-8 -*-
import os
import certifi
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "TestCertiDigital"
default_task = "publish"

os.environ['REQUESTS_CA_BUNDLE'] = "/Users/sergiosanchezherranz/certs/custom_cacerts.pem"


@init
def set_properties(project):
    pass
