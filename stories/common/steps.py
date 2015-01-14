#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lettuce import step, world
from utils import *
import fileinput
from os import path, remove
import MakeArduino
import serial

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
	# Verify the sketch selection
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'
	assert 'name' in world.c['sketch'], 'Internal error, no name in the sketch object.'

	# Substitute the tokens
	sketch_name = world.c['sketch']['name'] + '.ino'
	tmp_sketch_path = translate_sketch(sketch_name)

	# Prepare the compiler
	assert 'ide_version' in world.c, 'Internal error, no Arduino IDE version.'
	ide_path = get_config('IDEs.' + world.c['ide_version'] + '.Path')

	# Uploading
	assert 'hardware' in world.c, 'Internal error, no hardware defined.'
	port = get_config('Hardwares.' + world.c['hardware'] + '.port' )
	print port,tmp_sketch_path,ide_path
	c=MakeArduino.MakeArduino(port, 
		                      tmp_sketch_path,
		                      ide_path,
		                      "atmega328p",
		                      "arduino",
		                      "16000000L",
		                      "115200",
		                      "1", 
		                      1
		                      )	
	c.compileAndUpload()

	kind = world.c['sketch']['kind']

	if kind == 'unit test':
		try:            
			port=serial.Serial(port, 9600, timeout=1)
			response = obtain_arduino_response(port, 60)
			print response
			result = analysis_arduino_unit_test(response)

			world.result = not result['failed']
			world.result_detailed = result
		except Exception, argument:
			assert False, argument

@step(u'It is a success')
def it_is_a_success(step):
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'	
	kind = world.c['sketch']['kind']

	if kind == 'unit test':
		assert world.result, 'UNIT TEST FAILED: %s' % world.result_detailed['failed']
	else:
		# default
		assert world.result, 'UNKOWN ERROR'

@step(u'It is a failure')
def it_is_a_failure(step):
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'	
	kind = world.c['sketch']['kind']

	if kind == 'unit test':
		assert not world.result, 'UNIT TEST PASSED: %s' % world.result_detailed['passed']
	else:
		# default
		assert not world.result, 'UNKOWN ERROR'
