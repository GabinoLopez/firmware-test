Feature: SMS
  In order to validate that the current GSM library are able to manage SMS functionalities
  As Thinking Thing QA
  I'll send, receive, delete an SMS in TTOpen and GSM Shield HW

  @sms @sms-0001 @ready
  Scenario: Sending an SMS
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the example sketch "<sketch>"
    And considering the sequence "<sequence>"
    When I upload and run the sketch 
    Then It is a success

    Examples:
    | type      | version  | sequence    | sketch       |
    | Shield    | 1_0_x    | sendSMS     | SendSMS      |
    | Shield    | 1_5_x    | sendSMS     | SendSMS      |
    | TTOpen    | 1_0_x    | sendSMS     | SendSMS      |
    | TTOpen    | 1_5_x    | sendSMS     | SendSMS      |

