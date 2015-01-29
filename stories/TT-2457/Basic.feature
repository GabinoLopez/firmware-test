Feature: TT-2457 Unit Tests
  In order to validate that the current DataMap library are properly working
  As Thinking Thing QA
  I'll execute the full set of unit tests included

  @TT-2457 @unittests @ready @TT-2457-ut-0001
  Scenario: Run all the unit tests of TT-2457
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    When I run all the unit tests of TT-2457
    Then They are successful

    Examples:
    | type      | version  |
    | Shield    | 1_0_x    |
    | Shield    | 1_5_x    |
    | TTOpen    | 1_0_x    |
    | TTOpen    | 1_5_x    |

