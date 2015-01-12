Feature: SMS
  In order to validate that the current GSM library are able to manage SMS functionalities
  As Thinking Thing QA
  I'll send, receive, delete an SMS in TTOpen and GSM Shield HW

  @sms @sms-0001 @ready
  Scenario: Sending an SMS
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the test sketch "xend"
    When I upload and run the sketch 
    And I execute the sequence "<sequence>"
    Then It is a success

    Examples:
    | type      | version  | sequence    |
    | TTOpen    | 1.5.x    | sendSMS     |
    | Shield    | 1.5.x    | sendSMS     |
    | Shield    | 1.0.x    | sendSMS     |

