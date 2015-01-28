#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lettuce import step, world
from utils import *
import fileinput
from os import path, remove
import MakeArduino
import serial
import yaml

#
# Fixing parameters
#
@step(u'a hardware of type "([^"]*)"')
def a_hardware_of_type_group1(step, hardware):
	verify_config('Hardwares',hardware)
	world.c['hardware'] = hardware

@step(u'the Arduino IDE version "([^"]*)"')
def the_arduino_ide_version_group1(step, ide_version):
	verify_config('IDEs',ide_version)
	world.c['ide_version'] = ide_version

#
# Fixing sketches
#
@step(u'using the (.*) sketch "([^"]*)"')
def using_the_group1_sketch_group2(step, kind, sketch_name):
	if kind == 'example':
		# Case of arduino sketch
		world.c['sketch'] = {'path':verify_arduino_sketch(sketch_name),'name':sketch_name,'kind':kind}
	elif kind == 'test':
		# Case of local sketch
		verify_test_sketch(sketch_name)
		world.c['sketch'] = {'name':sketch_name, 'kind':kind}
	elif kind == 'unit test':
		# Case of unit test
		verify_unit_sketch(sketch_name)
		world.c['sketch'] = {'name':sketch_name, 'kind':kind}

@step(u'using the sketch "([^"]*)"')
def using_the_sketch_group1(step, sketch_name):
    # Case of local sketch
	verify_test_sketch(sketch_name)
	world.c['sketch'] = {'name':sketch_name, 'kind':'test'}

#
#  Selecting sequences
#
@step(u'considering the sequence "([^"]*)"')
def considering_the_sequence_group1(step, sequence):
	seq_path = path.join(path.dirname(__file__),"..","..","auxiliary","sequences",sequence + ".yaml")
	assert path.isfile(seq_path), 'Not found the file %s.' % seq_path
	with open(seq_path) as sequence_file:
		try:
			world.c['sequence'] = yaml.load(sequence_file)
		except Exception, argument:
			assert False, 'Problems reading %s: %s' % (sequence,argument)

#
#  Actions on the hardware
#
@step(u'I upload and run the sketch')
def i_upload_and_run_the_sketch(step):
	# Verify the sketch selection
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'
	kind = world.c['sketch']['kind']
	if kind != 'example':
		assert 'name' in world.c['sketch'], 'Internal error, no name in the sketch object.'

		# Substitute the tokens
		sketch_name = world.c['sketch']['name'] + '.ino'
		tmp_sketch_path = translate_sketch(sketch_name)
	else:
		assert 'path' in world.c['sketch'], 'Internal error, no name in the sketch object.'
		sketch_name = world.c['sketch']['name'] + '.ino'
		tmp_sketch_path = translate_sketch(sketch_name,origin=world.c['sketch']['path'])

	# Prepare the compiler
	assert 'ide_version' in world.c, 'Internal error, no Arduino IDE version.'
	ide_path = get_config('IDEs.' + world.c['ide_version'] + '.Path')
	ide_version = world.c['ide_version']

	# Uploading
	assert 'hardware' in world.c, 'Internal error, no hardware defined.'
	port = get_config('Hardwares.' + world.c['hardware'] + '.port' )
	hardware = world.c['hardware']
	arudino_timeout = get_config('Hardwares.' + world.c['hardware'] + '.timeout')

	c=MakeArduino.MakeArduino(port, 
		                      tmp_sketch_path,
		                      ide_path,
		                      "atmega328p",
		                      "arduino",
		                      "16000000L",
		                      "115200",
		                      "1", 
		                      False,
		                      version=ide_version,
		                      hw_platform=hardware
		                      )	
	compile_result, result_details = c.compileAndUpload()
	assert compile_result==0, "Problems compiling: %s-%s" % (compile_result,result_details)

	
	if kind == 'unit test':
		try:            
			port=serial.Serial(port, 9600, timeout=1)
			response = obtain_arduino_response_unit_test(port,arudino_timeout)
			result = analysis_arduino_unit_test(response)

			if not result['failed'] and not result['passed']:
				world.result = False
				world.result_detailed = 'No test result found in the response: %s' % response
			else:
				world.result = not result['failed']
				world.result_detailed = result
		except Exception, argument:
			assert False, argument
	elif kind == 'test' or kind == 'example':
		try:            
			port=serial.Serial(port, 9600, timeout=1)
			if 'sequence' in world.c:
				sequence = world.c['sequence']
				assert isinstance(sequence,list), 'Improperly defined sequence. It is not a list of objects.'
				step_counter = 0
				for step in sequence:
					assert isinstance(step,dict), 'Improperly defined sequence. The step %s is not an object' % step_counter
					assert 'output' in step, 'Improperly defined sequence. The step %s has not "out" field.' % step_counter
					desired_output = recall(step['output'])
					response = obtain_arduino_response(port,arudino_timeout, expected=desired_output)
					# print '<<', response
					step_counter += 1
					world.result = desired_output in response
					if not world.result:
						world.result_detailed = 'Not received %s in the response at step %s but %s.' % (desired_output,step_counter,response)
						break
					if 'input' in step:
						input = recall(step['input']+'\n')
						# print '>>', input 
						port.write(input)
				if world.result:
					world.result_detailed = 'All the steps verified.'
			else:
				world.c['output'] = obtain_arduino_response(port,arudino_timeout)
		except Exception, argument:
			assert False, argument		

#
#  Verifications
#
@step(u'It is a success')
def it_is_a_success(step):
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'	
	kind = world.c['sketch']['kind']

	if kind == 'unit test':
		if isinstance(world.result_detailed,dict):
			assert world.result, 'UNIT TEST FAILED: %s' % world.result_detailed['failed']
		else:
			assert world.result, 'NOT RESULT FOUND: %s' % world.result_detailed
	else:
		# default
		assert world.result, world.result_detailed

@step(u'It is a failure')
def it_is_a_failure(step):
	assert 'sketch' in world.c, 'No sketch has been declared in the feature. Review the feature.'
	assert 'kind' in world.c['sketch'], 'Internal error, no kind in the sketch object.'	
	kind = world.c['sketch']['kind']

	if kind == 'unit test':
		assert not world.result, 'UNIT TEST PASSED: %s' % world.result_detailed['passed']
	else:
		# default
		assert not world.result, world.result_detailed

@step(u'I verify the output against "([^"]*)"')
def i_verify_the_output_against_group1(step, output_file):
	assert 'output' in world.c, 'No output obtained yet.'
	desired_output = get_output(output_file + '.out').strip()
	world.result = desired_output in world.c['output'].strip()
	if not world.result:
		world.result_detailed = 'Expected "%s" and received "%s".' % (desired_output,world.c['output'])
	else:
		world.result_detailed = 'All it is correct.'
