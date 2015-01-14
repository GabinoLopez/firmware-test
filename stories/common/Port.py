"""
Created on 23/03/2012
Continuous Integration for Arduino SDK (Windows NT platform) 
@author: David Del Peral
    
This class is only designed for Windows platforms. It doesn't work on Unix environments.
"""

try:
    import serial
except ImportError, e:
    print("THIS PROGRAM NEEDS PySerial. Install it!")
    import sys
    sys.exit(-1)

class Port(object):
    """
    This class represents a serial port with state (0 -> free, 1 -> busy)
    """

    def __init__(self, name):
        """
        Constructor
        
        :param name: port name
        :type name: string
        """
        
        self.__portname = name # Port name
        self.__state = 0 # Port state (default: free)
                
    def getName(self):
        """
        Returns the port name
        
        :returns: port name
        :rtype: string
        """
        return self.__portname
    
    def getState(self):
        """
        Returns the port state
        
        :returns: port state
        :rtype: integer
        """
        return self.__state
    
    def changeState(self):
        """
        Change the port state to busy or free
        """
        if self.__state == 0:
            self.__state = 1
        else:
            self.__state = 0
    
    def testPort(self):
        """
        Test if the port is available
        
        :returns: true if the port is availabe, otherwise returns false
        :rtype: boolean
        """
        try:
            testport = serial.Serial(self.__portname)
            testport.close()
            return True
        except:
            return False
            