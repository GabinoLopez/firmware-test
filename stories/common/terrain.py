#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: japaz
# @Date:   2015-01-12 15:11:22
# @Last Modified by:   japaz
# @Last Modified time: 2015-01-28 14:41:22
from lettuce import before, after, world
import yaml
from os import path
from utils import clean_all_tmp_sketch

@before.all
def before_all():
	# Verbose mode flag
    world.vm = 1

    # Reading configuration
    with open(path.join(path.dirname(__file__),"..","..","conf","environment.yaml")) as config_file:
    	world.config = yaml.load(config_file)

   	# Deleting tmp sketch
   	clean_all_tmp_sketch()

@before.each_scenario
def setup_some_scenario(scenario):
	# To be sure that there is no configuration between features
	world.c = {}
	world.result = None
	world.result_detailed = None