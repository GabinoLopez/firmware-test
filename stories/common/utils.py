#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  A list of utils functions
#
from lettuce import world
from os import path, remove, rmdir, makedirs, walk
import re
import numbers
import shutil
from datetime import datetime
import sys

#
#  Patterns
#  
def find_in_map(cad,map):
	elements = cad.strip().split('.')
	for element in elements:
		if not element in map:
			return None
		map = map[element]

	return map

def recall(cad):
	'''
	This function takes a string, look for:

	1. <#tokens#>: for substituting it for a value in world.c
	2. <#config.tokens#>: for substituting it for a value in world.config
	3. some texts declared to be substituted in Sketchs --> Substitutions

	'''
	tp = re.compile(r'<#([A-Za-z0-9.]*)#>')

	sk_subs = 'Sketchs' in world.config and 'Substitutions' in world.config['Sketchs']

	possibles = tp.findall(cad)
	value = None
	for toChange in possibles:
		if toChange.startswith('config.'):
			value = find_in_map(toChange[7:],world.config)
		else:
			value = find_in_map(toChange,world.c)

		if not value and  sk_subs and toChange in world.config['Sketchs']['Substitutions']:
			value = world.config['Sketchs']['Substitutions'][toChange]

		if value and ( isinstance(value, numbers.Number)):
			value = str(value)

		if value and ( isinstance(value,str) or isinstance(value,unicode) ):
			cad = re.sub('<#' + toChange + '#>', value, cad)


	if sk_subs:
		for subs in world.config['Sketchs']['Substitutions']:
			cad = re.sub(subs,world.config['Sketchs']['Substitutions'][subs],cad)
	return cad

#
# Outputs management
#
def get_output(output_name):
	assert output_name.endswith('.out'), 'Improper output name, it should end in .out.'
	filepath = path.join(path.dirname(__file__),"..","..","auxiliary","outputs",output_name)
	assert path.isfile(filepath), 'No %s file found!' % (output_name)
	try:
		f = file(filepath,'r')
		output = f.read()
		f.close()
		return recall(output)
	except Exception, argument:
		assert False, 'Problems getting the file %s: %s' % (output_name,argument)	

#
#  Sketch management
#
def clean_all_tmp_sketch():
	dirpath_tmp = path.join(path.dirname(__file__),"..","..","auxiliary","sketches","tmp")
	if path.isdir(dirpath_tmp):
		shutil.rmtree(dirpath_tmp)
	makedirs(dirpath_tmp)

def translate_sketch(sketch_name,origin=None):
	assert sketch_name.endswith('.ino'), 'Improper sketch name, it should end in .ino.'
	first_part = sketch_name[:-4]
	if not origin:
		filepath_origin = path.join(path.dirname(__file__),"..","..","auxiliary","sketches",sketch_name)
	else:
		filepath_origin = origin
	filepath_tmp = path.join(path.dirname(__file__),"..","..","auxiliary","sketches","tmp",first_part,sketch_name)
	dirpath_tmp = path.join(path.dirname(__file__),"..","..","auxiliary","sketches","tmp",first_part)
	assert path.isfile(filepath_origin), 'No %s file found!' % (sketch_name)
	try:
		if path.isdir(dirpath_tmp):
			shutil.rmtree(dirpath_tmp)
		makedirs(dirpath_tmp)
		f_origin = file(filepath_origin,'r')
		f_dest = file(filepath_tmp,'w')
		for line in f_origin:
			changed = recall(line)
			f_dest.write(changed)
		f_dest.close()
		f_origin.close()
		return dirpath_tmp
	except Exception, argument:
		assert False, 'Problems changing the file %s: %s' % (sketch_name,argument)

def obtain_arduino_response_unit_test(port, tmax):
    tstart=datetime.now()
    input=""
    while True:
        tdelta=datetime.now()-tstart
        if tdelta.total_seconds()>tmax:
            break
        c = port.read()
        input+=c
        if "test(s)." in input:
            break
    return input

def obtain_arduino_response(port, tmax, expected = None):
    tstart=datetime.now()
    input=""
    while True:
        tdelta=datetime.now()-tstart
        if tdelta.total_seconds()>tmax:
            break
        c=port.read()
        input+=c
        if expected and expected in input:
            break
    return input

def analysis_arduino_unit_test(response):
	'''
	It takes the text result as:

	Assertion failed: (x=1) != (1=1), file sketch_jan14a.ino, line 12.
	Test incorrect failed.
	Test summary: 0 passed, 1 failed, and 0 skipped, out of 1 test(s).

	And it parses the message to obtain a list of structured tests and its results.
	'''
	lines = response.split('\n')
	passed = []
	failed = []
	assertion = []
	for line in lines:
		line = line.strip()
		if line.endswith('passed.'):
			passed.append(line[:-8])
		elif line.startswith('Assertion failed:'):
			assertion.append(line[17:])
		elif line.endswith('failed.'):
			failed.append({'test':line[:-8],'assertions':assertion})
			assertion = []

	return {'passed':passed, 'failed':failed}

#
#  Configuration files
#
def get_config(path):
	verify_config(path)
	return find_in_map(path,world.config)

def verify_map_option(name_map,map,path,value):
	''' 
	In a map verify if the value is one of the options
	in the path parsed as part.subpart.subsubpart --> list
	'''
	elements = path.strip().split('.')
	followed_path = []
	for element in elements:
		followed_path.append(element)
		assert element in map, 'Problem with %s. Section %s is required and not present.' % (name_map,'.'.join(followed_path))
		map = map[element]
	if value:
		assert value in map, 'Problem with %s. Value %s should to be present at %s and it is not.' % (name_map,value,followed_path.join('.'))

def verify_config(path,value=None):
	verify_map_option('environment.yaml file',world.config,path,value)	

#
#   Sketch files
#
def verify_test_sketch(sketch_file):
	assert path.isfile(path.join(path.dirname(__file__),"..","..","auxiliary","sketches",sketch_file + '.ino')), \
			'There is no file %s.ino in the path %s.' % (sketch_file,path.join(path.dirname(__file__),"..","..","auxiliary",'sketches'))

def verify_ino_in_path(origin,sketch_file):
	sketch_file += '.ino'
	for dirname, dirnames, filenames in walk(origin):
		# print path to all filenames.
		for filename in filenames:
			if filename.endswith(sketch_file):
				return dirname


def verify_arduino_sketch(sketch_file):
	assert 'ide_version' in world.c, 'Assert not Arduino version selected yet.'
	ide_path = get_config('IDEs.' + world.c['ide_version'] + '.Path')
	assert path.isdir(ide_path), 'Incorrect path to Arduino IDE: %s' % ide_path
	assert path.isdir(path.join(ide_path,'examples')), 'No examples directory in the Arduino IDE.'
	assert path.isdir(path.join(ide_path,'libraries')), 'No lib directory in the Arduino IDE.'
	found_in = verify_ino_in_path(path.join(ide_path,'examples'),sketch_file)
	if not found_in:
		found_in = verify_ino_in_path(path.join(ide_path,'libraries'),sketch_file)
	assert found_in, 'There is no sketch called %s.' % sketch_file
	assert path.isfile(path.join(found_in,sketch_file + '.ino')), 'There is no file %s.' % path.join(found_in,sketch_file + '.ino')
	return path.join(found_in,sketch_file + '.ino')

def verify_unit_sketch(sketch_file):
	assert path.isfile(path.join(path.dirname(__file__),"..","..","auxiliary","sketches",sketch_file + '.ino')), \
			'There is no file %s.ino in the path %s.' % (sketch_file,path.join(path.dirname(__file__),"..","..","auxiliary",'sketches'))
