"""
Created on 23/03/2012
Continuous Integration for Arduino SDK (Windows NT platform) 
@author: David Del Peral

This class is only designed for Windows platforms.
It doesn't work on Unix environments.
== ONLY COMPATIBLE WITH ARDUINO IDE 1.0.x (NOT 1.5.x) ==
== NOT COMPATIBLE FOR SKETCHS WITH .pde EXTENSION ==
"""

import subprocess
import os
import glob
import Library

class MakeArduino(object):
    """
    This class compile and upload an Arduino sketch.
    """
    
    def __init__(self, port, sketch, path_sdk, mcu, programmer, fcpu, burnrate, identification, verbose, version='1_0_x'):
        """
        Constructor
        
        :param port: serial port used for Arduino board
        :type port: string
        :param sketch: absolute path of the chosen sketch (sketch folder)
        :type sketch: string
        :param path_sdk: absolute path of the Arduino SDK 1.0 folder
        :type path_sdk: string
        :param mcu: Arduino board chip chosen
        :type mcu: string
        :param programmer: Arduino programmer chosen
        :type programmer: string
        :param fcpu: FCPU used
        :type fcpu: string
        :param burnrate: Burnrate for upload used
        :type burnrate: string
        :param identification: ID
        :type identification: string
        :param verbose: Verbose mode activation
        :type verbose: boolean
        """
        
        self.__includes = [] # List of libraries used by the sketch (objects Library)
        self.__libraries = [] # List of all available objects libraries (objects Library)

        self.__version = version
        
        # String for save later the absolute path of C++ code file generated with the sketch
        self.__cpp_path = ""
        # String for save later the absolute path of hexadecimal file generated with the sketch
        self.hex_path = ""
        
        self.__port = port # Port used
        self.__sketch = sketch # Sketch used (sketch folder)
        self.__path_sdk = path_sdk # Absolute path of Arduino SDK 1.0 used
        self.__mcu = mcu # Arduino board chip used
        self.__programmer = programmer # Programmer used
        self.__fcpu = fcpu # FCPU used
        self.__burnrate = burnrate # Burnrate for upload used
        self.__internalID = identification # ID
        
        self.__verbose = verbose
        
        # THE TEMP FOLDER CONTAINS ALL THE FILES GENERATED FOR UPLOAD THE SKETCH TO THE BOARD!!
        self.__sketch_temp = os.path.join(self.__sketch, 'temp') # Absolute path of temp folder for the sketch
        
        # Absolute path of tools for compilation and upload the sketch (includes with Arduino SDK)
        # THE CREATED PATH IS BASED ON THE ORGANIZATION OF THE ARDUINO SDK 1.0
        # == NOT VALID FOR PREVIOUS VERSIONS!! ==
        self.__tools_path = os.path.join(self.__path_sdk, "hardware", "tools", "avr", "bin")
        
        # Absolute path of sketch file (.ino)
        self.__ino_path = os.path.join(self.__sketch, (os.path.basename(self.__sketch) + '.ino'))
                
        # Absolute path of AVRDUDE configuration file
        self.__avrdude_configuration_file = os.path.join(self.__path_sdk, "hardware", "tools", "avr", "etc", "avrdude.conf")
    
    def __deleteTemp(self):
        """
        Deletes the 'temp' folder of the sketch
        """
        if os.path.isdir(self.__sketch_temp): 
            import shutil
            shutil.rmtree(self.__sketch_temp, True) # Delete the 'temp' folder recursively
    
    def __parserSketch(self):
        """
        Parse the sketch for remove comments and search for including libraries and existing functions
        
        :returns: 0 if the file is has parsed correctly, otherwise a negative number
        :rtype: integer
        """
        
        self.__searchLibraries() # Search all available libraries of Arduino SDK
        self.__deleteTemp() # Delete 'temp' folder if it exists
        os.mkdir(self.__sketch_temp) # Establish a new 'temp' folder
        
        try:
        
            # Open the file of the sketch and saves its contents in a variable
            fileOne = open(self.__ino_path, 'r')
            code = str(fileOne.read())
            fileOne.close()
             
            import re
            
            # Compile REGULAR EXPRESIONS for different searches
            re_comments1 = re.compile('(?<!/)\/\*[\s\S]*?\*\/')
            re_comments2 = re.compile('\/\/.*')
            re_header = re.compile('(#include(?:\\\\\\n|.)*)')
            re_functions = re.compile('(?:void|bool|char|int|unsigned int|signed int|unsigned char|signed char|boolean|byte)\s*\*?\s+\w+\s*\(.*\)\s*\{')
            
            # Clear all comments of code
            code = re.sub(re_comments1, "", code)
            code = re.sub(re_comments2, "", code)
            
            # Search for libraries used by the sketch (#include code lines)
            h_temp = re_header.findall(code)
            if len(h_temp) > 0:
                headers = [] # List to store the found includes (only header filename)
                for h in h_temp:
                    # Filter the found include code
                    h = str(h)
                    h = h.replace("#include <", "")
                    h = h.replace("#include \"", "")
                    h = h.replace(">", "")
                    h = h.replace("\"", "")
                    h = h.replace("\n", "")
                    h = h.strip()
                    headers.append(h)
                for h in headers:
                    # Check the library to which it belongs the header
                    # and see if it is already inserted in the list of libraries
                    # used by the sketch
                    res_search_lib = self.__searchCorrespondingLibray(h)
                    if res_search_lib != None:
                        if self.__addedLibrary(res_search_lib.getPath()) == False:
                            self.__includes.append(res_search_lib)
            
            # Search for all functions in the code (setup(), loop() and auxiliar functions)
            f_temp = re_functions.findall(code)
            if len(f_temp) > 0:
                functions = [] # List to store the found functions (type line: "<type> <function_name>(<params>) {") 
                for f in f_temp:
                    # Filter the found function line code
                    f = str(f)
                    f = f.replace("{", "")
                    f = f.replace("\n", "")
                    f = f.strip()
                    functions.append(f)
            
            # Open sketch file to store its lines of content in a variable        
            fileino = open(self.__ino_path, 'r')
            filenameino = os.path.split(self.__sketch)
            shortname = os.path.splitext(filenameino[1])
            codeino = fileino.readlines()
            fileino.close()
            
            # Create new C++ code file
            self.__cpp_path = os.path.join(self.__sketch_temp, shortname[0] + ".cpp")
            filecpp = open(self.__cpp_path, 'w+')
            filecpp.write('#include "Arduino.h"\n') # Write Arduino header for compiler
            filecpp.write('#define ID "' + self.__internalID + '"\n') # Write #define ID with internal ID assigned
            declaration_written = False
            # Write each line of code and search the last include line for
            # insert the declaration of each found function in the sketch
            for linecode in codeino:
                filecpp.write(str(linecode)) # Write a code line of the sketch in the C++ code file
                if len(h_temp) > 0:
                    if declaration_written == False:
                        # Compare the header found with the last stored header
                        if ("#include" in linecode) & (headers[len(headers)-1] in linecode):
                            # Write all declarations of functions
                            for f in functions:
                                filecpp.write(f + ";\n")
                            declaration_written = True
            filecpp.close()
            
            return 0
        
        except IOError:
            
            print("Parser open file error")
            return -1
                           
    def __compile_(self):
        """
        Compile the sketch and generate all files for upload it to Arduino board
        
        :returns: 0 if the sketch is has compiled correctly, otherwise a negative number
        :rtype: integer
        """
        
        res_parser = self.__parserSketch() # Call parser function
        if res_parser < 0:
            return -1   
           
        # Necessary elements paths (Arduino core library & Arduino board type configuration)
        if self.__version != '1_0_x':
            # 1_5_x or more
            cores_path = os.path.join(self.__path_sdk, "hardware", "arduino", "avr", "cores", "arduino")
            variants_standard_path = os.path.join(self.__path_sdk, "hardware", "arduino", "avr", "variants", "standard")       
        else:
            # 1_0_x, the old ones
            cores_path = os.path.join(self.__path_sdk, "hardware", "arduino", "cores", "arduino")
            variants_standard_path = os.path.join(self.__path_sdk, "hardware", "arduino", "variants", "standard")
        
        # All the basic commands of the tools (compilers, generators...) to run and its standard parameters for Arduino
        # -- ONLY INCLUDED ARDUINO ONE MODEL -- NOT TESTED WITH OTHER TYPES OF ARDUINO BOARD!!!
        cmd_avrgpp = os.path.join(self.__tools_path, "avr-g++") + " -c -g -Os -Wall -fno-exceptions -ffunction-sections -fdata-sections -mmcu=" + self.__mcu + " -DF_CPU=" + self.__fcpu + " -DARDUINO=105"
        cmd_avrgcc_lib = os.path.join(self.__tools_path, "avr-gcc") + " -c -g -Os -Wall -ffunction-sections -fdata-sections -mmcu=" + self.__mcu + " -DF_CPU=" + self.__fcpu + " -DARDUINO=105"
        cmd_avrar = os.path.join(self.__tools_path, "avr-ar") + " rcs"
        cmd_avrgcc_core = os.path.join(self.__tools_path, "avr-gcc") + " -Os -Wl,--gc-sections -mmcu=" + self.__mcu
        cmd_avrobjcopy1 = os.path.join(self.__tools_path, "avr-objcopy") + " -O ihex -j .eeprom --set-section-flags=.eeprom=alloc,load --no-change-warnings --change-section-lma .eeprom=0"
        cmd_avrobjcopy2 = os.path.join(self.__tools_path, "avr-objcopy") + " -O ihex -R .eeprom"
            
        #############################################################    
        # ----- GENERATE FINAL SHELL COMMANDS AND EXECUTE ITS ----- #
        #############################################################
        
        # NOTE: The output console will hide, unless an error with any command occurs.
                  
        # -- Compilation of the sketch -- #
        # ------------------------------- #
               
        # Establish compiled object path
        obj_sketch_path = self.__cpp_path + ".o"
        # Create the final command of execution of avr-g++
        command_build_sketch = cmd_avrgpp + " -I" + cores_path + " -I" + variants_standard_path
        # Add the paths of libraries includes in the compiler command
        for dependency in self.__includes:
            command_build_sketch += " -I" + dependency.getPath()
        # Finalize compiler command
        command_build_sketch += " " + self.__cpp_path + " -o" + obj_sketch_path
        if self.__verbose:
            print(self.__debugMsg() + "BUILDING SKETCH...")
        
        # Launch the avr-g++ command in a subprocess pipe
        pipe = subprocess.Popen(command_build_sketch, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_console = str(pipe.communicate()[1])
        # Scan the console output for detect any error
        # print "Output Console:", output_console
        if ("error" in output_console) | ("failed" in output_console):
            print(self.__debugMsg() + command_build_sketch)
            print(self.__debugMsg() + output_console)
            return -2
    
        # -- Compilation of include libraries -- #
        # -------------------------------------- #
        
        objlibs = [] # Paths of library compiled objects 
        
        if self.__verbose:
            print(self.__debugMsg() + "BUILDING INCLUDE LIBS...")
        
        for lib in self.__includes:
            # Compile C code files of libraries
            for cfile in lib.getCFiles():
                # Create the final command of execution of avr-gcc
                command_build_includes_lib = cmd_avrgcc_lib + " -I" + cores_path
                command_build_includes_lib += " -I" + variants_standard_path
                # Add the paths of libraries in the compiler command
                for dependency in self.__includes:
                    command_build_includes_lib += " -I" + dependency.getPath()
                # Finalize compiler command
                command_build_includes_lib += " -I" + os.path.join(lib.getPath(), "utility")
                command_build_includes_lib += " " + cfile + " -o" + os.path.join(self.__sketch_temp, os.path.split(cfile)[1] + ".o")
                # Establish compiled object path and add to the list
                objlibs.append(os.path.join(self.__sketch_temp, os.path.split(cfile)[1] + ".o"))
                # Launch the avr-gcc command in a subprocess pipe
                pipe = subprocess.Popen(command_build_includes_lib, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output_console = str(pipe.communicate()[1])
                # Scan the console output for detect any error
                if ("error" in output_console) | ("failed" in output_console):
                    print(self.__debugMsg() + command_build_includes_lib)
                    print(self.__debugMsg() + output_console)
                    return -3
            # Compile C++ code files of libraries
            for cppfile in lib.getCppFiles():
                # Create the final command of execution of avr-g++
                command_build_includes_lib = cmd_avrgpp + " -I" + cores_path
                command_build_includes_lib += " -I" + variants_standard_path
                # Add the paths of libraries in the compiler command
                for dependency in self.__includes:
                    command_build_includes_lib += " -I" + dependency.getPath()
                # Finalize compiler command
                command_build_includes_lib += " -I" + os.path.join(lib.getPath(), "utility")
                command_build_includes_lib += " " + cppfile + " -o" + os.path.join(self.__sketch_temp, os.path.split(cppfile)[1] + ".o")
                # Establish compiled object path and add to the list
                objlibs.append(os.path.join(self.__sketch_temp, os.path.split(cppfile)[1] + ".o"))
                # Launch the avr-g++ command in a subprocess pipe
                pipe = subprocess.Popen(command_build_includes_lib, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output_console = str(pipe.communicate()[1])
                # Scan the console output for detect any error
                if ("error" in output_console) | ("failed" in output_console):
                    print(self.__debugMsg() + command_build_includes_lib)
                    print(self.__debugMsg() + output_console)
                    return -4
        
        # -- Compilation of Arduino core libraries -- #
        # ------------------------------------------- #
        
        # Establish compiled objects path
        core_cfiles = glob.glob(os.path.join(cores_path, '*.c'))
        core_cppfiles = glob.glob(os.path.join(cores_path, '*.cpp'))
        
        core_objfiles = [] # Paths of core libraries compiled object files
        
        if self.__verbose:
            print(self.__debugMsg() + "BUILDING ARDUINO LIBS...")
        
        # Compile C code files of libraries
        for cfile in core_cfiles:
            # Create the final command of execution of avr-gcc
            command_build_core = cmd_avrgcc_lib + " -I" + cores_path
            command_build_core += " -I" + variants_standard_path
            command_build_core += " " + cfile + " -o" + os.path.join(self.__sketch_temp, os.path.split(cfile)[1] + ".o")
            # Establish compiled object path and add to the list
            core_objfiles.append(os.path.join(self.__sketch_temp, os.path.split(cfile)[1] + ".o"))
            # Launch the avr-gcc command in a subprocess pipe
            pipe = subprocess.Popen(command_build_core, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_console = str(pipe.communicate()[1])
            # Scan the console output for detect any error
            if ("error" in output_console) | ("failed" in output_console):
                print(self.__debugMsg() + command_build_core)
                print(self.__debugMsg() + output_console)
                return -5
        # Compile C++ code files of libraries
        for cppfile in core_cppfiles:
            # Create the final command of execution of avr-g++
            command_build_core = cmd_avrgpp + " -I" + cores_path
            command_build_core += " -I" + variants_standard_path
            command_build_core += " "  + cppfile + " -o" + os.path.join(self.__sketch_temp, os.path.split(cppfile)[1] + ".o")
            # Establish compiled object path and add to the list
            core_objfiles.append(os.path.join(self.__sketch_temp, os.path.split(cppfile)[1] + ".o"))
            # Launch the avr-g++ command in a subprocess pipe
            pipe = subprocess.Popen(command_build_core, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_console = str(pipe.communicate()[1])
            # Scan the console output for detect any error
            if ("error" in output_console) | ("failed" in output_console):
                print(self.__debugMsg() + command_build_core)
                print(self.__debugMsg() + output_console)
                return -6
        
        # -- Creation of core.a file -- #
        # ----------------------------- #
        
        if self.__verbose:
            print(self.__debugMsg() + "CREATING CORE EEP/ELF/HEX...")
        
        # Establish core.a path
        core_a_path = os.path.join(self.__sketch_temp, "core.a")
        # Create core from libraries compiled object files         
        for objfile in core_objfiles:
            # Create the final command of execution of avr-ar
            command_create_core = cmd_avrar + " " + core_a_path
            command_create_core += " " + objfile
            # Launch the avr-ar command in a subprocess pipe
            pipe = subprocess.Popen(command_create_core, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_console = str(pipe.communicate()[1])
            # Scan the console output for detect any error
            if ("error" in output_console) | ("failed" in output_console):
                print(self.__debugMsg() + command_create_core)
                print(self.__debugMsg() + output_console)
                return -7
                
        # -- Creation of ELF file -- #
        # -------------------------- #
        
        # Establish ELF file path
        elf_path = os.path.join(self.__sketch_temp, self.__cpp_path + ".elf")
        # Create the final command of execution of avr-gcc
        command_create_elf = cmd_avrgcc_core + " -o " + elf_path + " " + obj_sketch_path
        for obj in objlibs:
            command_create_elf += " " + obj
        command_create_elf += " " + core_a_path + " -L" + self.__sketch_temp + " -lm"
        # Launch the avr-gcc command in a subprocess pipe
        pipe = subprocess.Popen(command_create_elf, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_console = str(pipe.communicate()[1])
        # Scan the console output for detect any error
        if ("error" in output_console) | ("failed" in output_console):
            print(self.__debugMsg() + command_create_elf)
            print(self.__debugMsg() + output_console)
            return -8

        # -- Creation of EEP file -- #
        # -------------------------- #
        
        # Establish EEP file path
        eep_path = os.path.join(self.__sketch_temp, self.__cpp_path + ".eep")
        # Create the final command of execution of avr-objcopy
        command_create_eep = cmd_avrobjcopy1 + " " + elf_path + " " + eep_path
        # Launch the avr-objcopy command in a subprocess pipe
        pipe = subprocess.Popen(command_create_eep, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_console = str(pipe.communicate()[1])
        # Scan the console output for detect any error
        if ("error" in output_console) | ("failed" in output_console) | ("No such file" in output_console):
            print(self.__debugMsg() + command_create_eep)
            print(self.__debugMsg() + output_console)
            return -9

        # -- Creation of hexadecimal file -- #
        # ---------------------------------- #
        
        # Establish hexadecimal file path
        self.hex_path = os.path.join(self.__sketch_temp, self.__cpp_path + ".hex")
        # Create the final command of execution of avr-objcopy
        command_create_hexadecimal = cmd_avrobjcopy2 + " " + elf_path + " " + self.hex_path
        # Launch the avr-objcopy command in a subprocess pipe
        pipe = subprocess.Popen(command_create_hexadecimal, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_console = str(pipe.communicate()[1])
        # Scan the console output for detect any error
        if ("error" in output_console) | ("failed" in output_console) | ("No such file" in output_console):
            print(self.__debugMsg() + command_create_hexadecimal)
            print(self.__debugMsg() + output_console)
            return -10
        
        return 0
        
    def __upload(self):
        """
        Send the sketch to Arduino board and programm the microcontroller
        
        :returns: 0 if the sketch is has uploaded correctly, otherwise a negative number
        :rtype: integer
        """

        if self.__verbose:
            print(self.__debugMsg() + "UPLOADING...")
        
        # Create the command of execution of avrdude with it first parameters
        cmd_avrdude_parameters = os.path.join(self.__tools_path, "avrdude") + " -C" + self.__avrdude_configuration_file + " -p" + self.__mcu + " -c" + self.__programmer + " -P" + "\\\\.\\" + self.__port + " -b" + self.__burnrate + " -D"
        # Complete the command with hexadecimal file path and it last parameters
        cmd_avrdude_hex = " -Uflash:w:" + self.hex_path + ":i"
       
        # Create the final command of execution of avrdude
        command_upload = cmd_avrdude_parameters + cmd_avrdude_hex
        
        # Launch the avrdude command in a subprocess pipe
        pipe = subprocess.Popen(command_upload, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_console = str(pipe.communicate()[1])
        # Scan the console output for detect any error
        if ("not in sync" in output_console) | (("error" in output_console) | ("failed" in output_console)):
            print(self.__debugMsg() + output_console)
            return -1

        return 0
        
    def compileAndUpload(self):
        """
        Compile and upload to Arduino the sketch
        
        :returns: 0 if the sketch is has compiled and uploaded correctly, otherwise a negative number
        :rtype: integer
        """
        
        res_compilation = self.__compile_() # Compile sketch
        
        # Compile error control
        if res_compilation == 0:
            if self.__verbose:
                print(self.__debugMsg() + "Compilation OK!")
        elif res_compilation == -1:
            return res_compilation, self.__debugMsg() + "PARSER SKETCH ERROR!"
        elif res_compilation == -2:
            return res_compilation, self.__debugMsg() + "SKETCH COMPILATION ERROR!"
        elif res_compilation == -3:
            return res_compilation, self.__debugMsg() + "LIBRARY COMPILATION ERROR! (C CODE)"
        elif res_compilation == -4:
            return res_compilation, self.__debugMsg() + "LIBRARY COMPILATION ERROR! (C++ CODE)"
        elif res_compilation == -5:
            return res_compilation, self.__debugMsg() + "CORE LIBRARY COMPILATION ERROR! (C CODE)"
        elif res_compilation == -6:
            return res_compilation, self.__debugMsg() + "CORE LIBRARY COMPILATION ERROR! (C++ CODE)"
        elif res_compilation == -7:
            return res_compilation, self.__debugMsg() + "FAILED TO CREATE core.a!"
        elif res_compilation == -8:
            return res_compilation, self.__debugMsg() + "FAILED TO CREATE ELF FILE!"
        elif res_compilation == -9:
            return res_compilation, self.__debugMsg() + "FAILED TO CREATE EEP FILE"
        elif res_compilation == -10:
            return res_compilation, self.__debugMsg() + "FAILED TO CREATE HEXADECIMAL FILE"
        else:
            return -99, self.__debugMsg() + "UNEXPECTED ERROR!! PANIC!!"
        
        res_upload = self.__upload() # Upload the sketch to Arduino board
        
        # Upload error control
        if res_upload < 0:
            return -11, self.__debugMsg() + "UPLOAD ERROR!"
        else:
            if self.__verbose:
                print(self.__debugMsg() + "Upload OK!")
        
        return 0, "Upload OK"
            
    def __searchLibraries(self):
        """
        Search all available libraries in Arduino IDE library folder and store their paths
        """
        # Build Arduino IDE libraries path
        path_lib = os.path.join(self.__path_sdk, "libraries")
        # Search libraries subfolders
        subfolders = [f for f in os.listdir(path_lib) if os.path.isdir(os.path.join(path_lib, f))]
        if len(subfolders) > 0:
            # Build the absolute path of each library folder
            subfolders = [os.path.join(path_lib, f) for f in subfolders]
            for subdir in subfolders:
                # Create new object of class Library for each library subfolder
                if self.__version != '1_0_x':
                    lib_temp = Library.Library(os.path.join(subdir,'src'))
                else:
                    lib_temp = Library.Library(subdir)
                self.__libraries.append(lib_temp) # Store library name (subfolder name)
                                
    def __searchCorrespondingLibray(self, header_include):
        """
        Searches the corresponding library for a header include code
        
        :param header_include: header include code
        :type header_include: string
        :returns: corresponding library if it exists, otherwise return none object
        :rtype: Library object or None
        """
        for lib in self.__libraries:
            # Search a file with included filename in the header include code
            if lib.existsFile(header_include) == True:
                return lib
        return None

    def __addedLibrary(self, name):
        """           
        Determines if a library already added by another header
        
        :param name: path of library
        :type name: string
        :returns: true if the library already added, otherwise return false
        :rtype: boolean
        """
        
        for lib in self.__includes:
            if lib.getPath() == name:
                return True
        return False

    def __debugMsg(self):
        """
        Returns a string with sketch name and used port
        
        :returns: string with sketch name and used port
        :rtype: string
        """   
        return "MAKE MSG: " + os.path.splitext(os.path.split(self.__sketch)[1])[0] + " IN " + self.__port + ": "