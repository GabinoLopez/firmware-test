#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: japaz
# @Date:   2015-01-12 15:11:22
# @Last Modified by:   japaz
# @Last Modified time: 2015-01-12 20:26:43
from lettuce import before, after, world
import yaml
from os import path

@before.all
def before_all():
	# Verbose mode flag
    world.vm = 1

    # Reading configuration
    with open(path.join(path.dirname(__file__),"..","..","conf","environment.yaml")) as config_file:
            world.config = yaml.load(config_file)

@before.each_feature
def each_feature(feature):
	# To be sure that there is no configuration between features
    world.c = {}