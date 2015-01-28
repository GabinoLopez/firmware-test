Feature: Basic
  In order to check a device
  As Thinking Thing QA
  I'll send and execute three kind of basic tests

  @smoke @smoke-0001 @ready
  Scenario: Executing an empty unit test
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the unit test sketch "<unit test>"
    When I upload and run the sketch 
    Then It is a success

    Examples:
    | type      | version  |  unit test |
    | TTOpen    | 1_0_x    | xend       |
    | TTOpen    | 1_5_x    | xend       |
    | Shield    | 1_0_x    | xend       |
    | Shield    | 1_5_x    | xend       |

  @smoke @smoke-0002 @ready
  Scenario: Executing an empty specific test
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the sketch "<sketch>"
    And considering the sequence "<sequence>"
    When I upload and run the sketch
    Then It is a success

    Examples:
    | type      | version  | sequence  | sketch |
    | TTOpen    | 1_0_x    | hola      | hola   |
    | TTOpen    | 1_5_x    | hola      | hola   |
    | Shield    | 1_0_x    | hola      | hola   |
    | Shield    | 1_5_x    | hola      | hola   |

  @smoke @smoke-0003 @ready
  Scenario: Failing an empty specific test
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the sketch "<sketch>"
    And considering the sequence "<sequence>"
    When I upload and run the sketch
    Then It is a failure

    Examples:
    | type      | version  | sequence  | sketch |
    | TTOpen    | 1_0_x    | failed    | hola   |
    | TTOpen    | 1_5_x    | failed    | hola   |
    | Shield    | 1_0_x    | failed    | hola   |
    | Shield    | 1_5_x    | failed    | hola   |

  @smoke @smoke-0004 @ready
  Scenario: Executing an Arduino Sample
    Given a hardware of type "<type>"
    And the Arduino IDE version "<version>"
    And using the example sketch "<sample>"
    And considering the sequence "<sequence>"
    When I upload and run the sketch
    Then It is a success

    Examples:
    | type      | version  | sequence   | sample              |
    | TTOpen    | 1_0_x    | asciitable | ASCIITable          |
    | TTOpen    | 1_5_x    | asciitable | ASCIITable          |
    | TTOpen    | 1_0_x    | zero       | DigitalReadSerial   |
    | TTOpen    | 1_5_x    | zero       | DigitalReadSerial   |
    | Shield    | 1_0_x    | asciitable | ASCIITable          |
    | Shield    | 1_5_x    | asciitable | ASCIITable          |
    | Shield    | 1_0_x    | one        | DigitalReadSerial   |
    | Shield    | 1_5_x    | one        | DigitalReadSerial   |

