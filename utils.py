#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os


def basename(filename):
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]
