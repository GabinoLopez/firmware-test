# -*- coding: utf-8 -*-
from lettuce import step

@step(u'Given a hardware of type "([^"]*)"')
def given_a_hardware_of_type_group1(step, group1):
    assert False, 'This step must be implemented'

@step(u'And the Arduino IDE version "([^"]*)"')
def and_the_arduino_ide_version_group1(step, group1):
    assert False, 'This step must be implemented'

@step(u'And using the example sketch "([^"]*)"')
def and_using_the_example_sketch_group1(step, group1):
    assert False, 'This step must be implemented'

@step(u'When I upload and run the sketch')
def when_i_upload_and_run_the_sketch(step):
    assert False, 'This step must be implemented'

@step(u'And I execute the sequence "([^"]*)"')
def and_i_execute_the_sequence_group1(step, group1):
    assert False, 'This step must be implemented'
    
@step(u'Then It is a success')
def then_it_is_a_success(step):
    assert False, 'This step must be implemented'