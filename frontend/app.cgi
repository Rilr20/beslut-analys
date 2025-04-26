#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
A CGI-script for python, including error handling.
"""
import traceback
from wsgiref.handlers import CGIHandler
from app import app

try:
    CGIHandler().run(app)

except Exception as e: #pylint: disable=broad-except
    print("Content-Type: text/plain;charset=utf-8")
    print("")
    print(traceback.format_exc())