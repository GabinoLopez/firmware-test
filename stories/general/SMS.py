# -*- coding: utf-8 -*-
from lettuce import step, world

@step(u'And I execute the sequence "([^"]*)"')
def and_i_execute_the_sequence_group1(step, group1):
	world.result = True
	assert False, 'This step must be implemented'
    
@step(u'Then It is a success')
def then_it_is_a_success(step):
	assert world.result, 'Problem found'

@step(u'Then It is a failure')
def then_it_is_a_failure(step):
    assert False, 'This step must be implemented'