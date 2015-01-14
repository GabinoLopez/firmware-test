#include "Arduino.h"
#define ID "1"
/*

    Here a token TTOpen <#config.kk#> 763476473643376437 xend

    telefonica.com

*/

#include <ArduinoUnit.h>
void setup();
void loop();

/* test(correct)
{
  int x=1;
  assertEqual(x,1);
} */

test(incorrect)
{
  int x=1;
  assertNotEqual(x,1);
}

void setup()
{
  Serial.begin(9600);
  while(!Serial); // for the Arduino Leonardo/Micro only
}

void loop()
{
  Test::run();
}
