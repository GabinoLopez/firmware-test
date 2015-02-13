"""
Created on 03/04/2014
Factory script to extract ICCID & IMEI and charge Internal ID
@author: David Del Peral
"""

try:
    import serial
except ImportError, e:
    print("THIS PROGRAM NEEDS PySerial. Install it!")
    import sys
    sys.exit(-1)
    
import threading
import time

class Monitor(threading.Thread):
    """
    This class represents and launch a thread for monitoring the serial output connected to Thinking Things Core.
    """
    
    def __init__(self, arduino_port, core):
        """
        Constructor
        
        :param arduino_port: serial port to monitoring
        :type arduino_port: Port object
        :param core: representation of a core module
        :type Core: Core class object
        """
        
        # Thread initialization
        threading.Thread.__init__(self)

        self.__time_max = 60 # Maximum time for waiting 'SUCCESS' response from Arduino
        self.__baudrate = 9600 # Baudrate of serial port

        self.__port = arduino_port # Serial port
        self.__core = core # Core object        
        
        self.monitorResult = -2
            
    def run(self):
        
        # Opening serial port
        s = serial.Serial(self.__port.getName(), baudrate=self.__baudrate)
        s.flushOutput();
                
        monitoring = True
        
        # 0 => START CASE!
        # 1 => ICCID PASSED!
        # 2 => IMEI PASSED!
        # 3 => EEPROM RECORDING PASSED!
        casePassed = 0
        
        tagICCID = "ICCID|"
        tagIMEI = "IMEI|"
        tagID = "ID-READ|"
        
        errorMessages = ["E-START-MODEM", "E-ATE0", "E-LENGTH", "E-CHAR-ID", "ERROR"]
        
        time_start = time.time()
        
        while monitoring and (time.time() - time_start) < self.__time_max:
            
            try:
                data = s.readline()
            except:
                print("Serial exception: aborting...")
                self.monitorResult = -3
                monitoring = False
                break
            
            data = str(data)
            #print(data)
            data = data.replace("\r", '')
            data = data.replace("\n", '')
            data = data.replace(" ", '')
            
            # Check and save ICCID & IMEI,
            # also check EEPROM process,
            # everything in strict order.
            if casePassed == 0:
                
                if tagICCID in data:
                    if self.__core.setICCID(data.split("|")[1]):
                        casePassed += 1
                    else:
                        print("ERROR: ICCID corrupted")
                        self.monitorResult = -1
                        monitoring = False
                
                elif tagIMEI in data:
                    print("ERROR: IMEI early")
                    self.monitorResult = -1
                    monitoring = False
                
                elif tagID in data:
                    print("ERROR: ID early")
                    self.monitorResult = -1
                    monitoring = False
                    
            elif casePassed == 1:
                
                if tagICCID in data:
                    print("ERROR: ICCID early")
                    self.monitorResult = -1
                    monitoring = False
                    
                elif tagIMEI in data:
                    if self.__core.setIMEI(data.split("|")[1]):
                        casePassed += 1
                    else:
                        print("ERROR: IMEI corrupted")
                        self.monitorResult = -1
                        monitoring = False
                    
                elif tagID in data:
                    print("ERROR: ID early")
                    self.monitorResult = -1
                    monitoring = False
                    
            elif casePassed == 2:
                
                if tagICCID in data:
                    print("ERROR: ICCID early")
                    self.monitorResult = -1
                    monitoring = False
                    
                elif tagIMEI in data:
                    print("ERROR: IMEI early")
                    self.monitorResult = -1
                    monitoring = False
                    
                elif tagID in data:
                    if self.__core.getID() == data.split("|")[1]:
                        self.monitorResult = 0
                        monitoring = False
                        casePassed += 1
                    else:
                        print("ERROR: EEPROM content corrupted")
                        self.monitorResult = -1
                        monitoring = False
                    
            # Check if an error happened
            for failMessage in errorMessages:
                if failMessage in data:
                    print("ERROR: Message %s" % failMessage)
                    self.monitorResult = -1
                    monitoring = False

        s.close()
        