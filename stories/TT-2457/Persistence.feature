Feature: TT-2457 Persistence tests
  In order to validate that the current DataMap library is able to persist data
  As Thinking Thing QA
  I'll execute the full set of tests

  @TT-2457 @ready @TT-2457-persis-0001
  Scenario: Writing and reading from the remote database
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the example sketch "ReadWriteTTCloud"
    When I upload and run the sketch 
    Then It is a success

    Examples:
    | type              | version  |
    | TTOpen            | 1_5_x    |
    | TTOpen            | 1_0_x    |
    | Shield            | 1_5_x    |
    | Shield            | 1_0_x    |
    # | EthernetShield    | 1.5.x    |    
    # | EthernetShield    | 1.0.x    |


  @TT-2457 @ready @TT-2457-persis-0002
  Scenario: Writing and reading from the local memory
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the example sketch "ReadWriteTTMemory"
    When I upload and run the sketch 
    Then It is a success
	
    Examples:
    | type              | version  |
    | TTOpen            | 1_5_x    |
    | TTOpen            | 1_0_x    |

