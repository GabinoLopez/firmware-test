Feature: WebClient
  In order to validate that the current GSM library are able to execute a Web Client
  As Thinking Thing QA
  I'll connect a HTTP connection to a web server and GET information

  @gsmwebclient @gsmwebclient-0001 @ready
  Scenario: Executing the web client
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the example sketch "<sketch>"
    And considering the sequence "<sequence>"
    When I upload and run the sketch 
    Then It is a success

    Examples:
    | type      | version  | sequence    | sketch       |
    | Shield    | 1_0_x    | GsmWebClient     | GsmWebClient      |
    | Shield    | 1_5_x    | GsmWebClient     | GsmWebClient      |
#    | TTOpen    | 1_0_x    | GsmWebClient     | GsmWebClient      |
#    | TTOpen    | 1_5_x    | GsmWebClient     | GsmWebClient      |

