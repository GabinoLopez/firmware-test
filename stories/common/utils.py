#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  A list of utils functions
#
from lettuce import world
from os import path
import re
import numbers

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
#  Configuration files
#
def verify_map_option(name_map,map,path,value):
	''' 
	In a map verify if the value is one of the options
	in the path parsed as part.subpart.subsubpart --> list
	'''
	elements = path.strip().split('.')
	followed_path = []
	for element in elements:
		followed_path.append(element)
		assert element in map, 'Problem with %s. Section %s is required and not present.' % (name_map,followed_path.join('.'))
		map = map[element]
	assert value in map, 'Problem with %s. Value %s should to be present at %s and it is not.' % (name_map,value,followed_path.join('.'))

def verify_config(path,value):
	verify_map_option('environment.yaml file',world.config,path,value)	



#
#   Sketch files
#
def verify_test_sketch(sketch_file):
	assert path.isfile(path.join(path.dirname(__file__),"..","..","auxiliary","sketches",sketch_file + '.ino')), \
			'There is no file %s.ino in the path %s.' % (sketch_file,path.join(path.dirname(__file__),"..","..","auxiliary",'sketches'))


def verify_arduino_sketch(sketch_file):
	assert path.isfile(path.join(path.dirname(__file__),"..","..","auxiliary","sketches",sketch_file + '.ino')), \
			'There is no file %s.ino in the path %s.' % (sketch_file,path.join(path.dirname(__file__),"..","..","auxiliary",'sketches'))

def verify_unit_sketch(sketch_file):
	assert path.isfile(path.join(path.dirname(__file__),"..","..","auxiliary","sketches",sketch_file + '.ino')), \
			'There is no file %s.ino in the path %s.' % (sketch_file,path.join(path.dirname(__file__),"..","..","auxiliary",'sketches'))
