#include "Arduino.h"
#define ID "1"
#include <DataMap.h>
#include <ArduinoUnit.h>
void setup();
void loop();

DataMap DM;

void setup() {
  // initialize serial communications
  Serial.begin(9600);
}


test(lenght_before) {
  int size = DM.getSize();
  assertEqual(size,0);
}

test(adding) {
  bool b1 = DM.add("sensor0", "4573 - YES");
  bool b2 = DM.add("temperature", "25.8");
  bool b3 = DM.add("location" , "4234.34234, 2895.234");

  assertEqual(b1 && b2 && b3, true);
}

test(lenght_after) {
  int size = DM.getSize();
  assertEqual(size,3);
}

test(getting) {
  String s;
  s = DM.lookup("sensor0");
  
  bool b = s.equals("4573 - YES");
  assertEqual(b,true);
}


test(getting2) {
  String s;
  s = DM.lookup("location");
  s += DM.lookup("temperature");
  
  bool b = s.equals("4234.34234, 2895.23425.8");
  assertEqual(b,true);
}

test(removing) {
  DM.remove("temperature");
  String s;
  s = DM.lookup("temperature");
  
  bool b = s.equals("NOT FOUND") && (DM.getSize() == 2);
  assertEqual(b,true);
}

void loop() { 
  Test::run(); 
}
