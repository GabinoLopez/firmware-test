#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lettuce import step, world
from utils import verify_config, verify_arduino_sketch, verify_unit_sketch, verify_test_sketch, recall
import fileinput
from os import path

@step(u'a hardware of type "([^"]*)"')
def a_hardware_of_type_group1(step, hardware):
	verify_config('Hardwares',hardware)
	world.c['hardware'] = hardware

@step(u'the Arduino IDE version "([^"]*)"')
def the_arduino_ide_version_group1(step, ide_version):
	verify_config('IDEs',ide_version)
	world.c['ide_version'] = ide_version

@step(u'using the (.*) sketch "([^"]*)"')
def using_the_group1_sketch_group2(step, kind, sketch_name):
	if kind == 'example':
		# Case of arduino sketch
		verify_arduino_sketch(sketch_name)
	elif kind == 'test':
		# Case of local sketch
		verify_test_sketch(sketch_name)
	elif kind == 'unit test':
		# Case of unit test
		verify_unit_sketch(sketch_name)
	world.c['sketch'] = {'name':sketch_name, 'kind':kind}

@step(u'I upload and run the sketch')
def i_upload_and_run_the_sketch(step):
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'
	assert 'name' in world.c['sketch'], 'Internal error, no name in the sketch object.'
	filepath = path.join(path.dirname(__file__),"..","..","auxiliary","sketches",world.c['sketch']['name'] + '.ino') 
	print filepath
	for line in fileinput.input(filepath):
		print recall(line)
	assert False, 'This step must be implemented'