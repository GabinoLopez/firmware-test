# -*- coding: utf-8 -*-
from lettuce import step, world

@step(u'And I execute the sequence "([^"]*)"')
def and_i_execute_the_sequence_group1(step, group1):
	world.result = True
    
