"""
Created on 29/03/2012
Continuous Integration for Arduino SDK (Windows NT platform) 
@author: David Del Peral
"""

import os
import glob

class Library(object):
    """
    This class represents a library imported into the sketch by the directive include
    """
    
    def __init__(self, library_path):
        """
        Constructor
        
        :param library_path: absolute path of the library folder
        :type library_path: string
        """
            
        # Initialization of the attributes of the class   
        self.__path = library_path # Absolute path of the library in a string
        self.__headerfiles = [] # List to save later the absolute paths of headers found in the library folder
        self.__codecppfiles = [] # List to save later the absolute paths of C++ code files found in the library folder
        self.__codeansicfiles = [] # List to save later the absolute paths of ANSI C code files found in the library folder
        
        # Searches for every file type that make up the library
        self.__folderRunner(self.__path, self.__headerfiles, '*.h')
        self.__folderRunner(self.__path, self.__headerfiles, '*.hh')
        self.__folderRunner(self.__path, self.__headerfiles, '*.hpp')
        self.__folderRunner(self.__path, self.__codecppfiles, '*.cpp')
        self.__folderRunner(self.__path, self.__codecppfiles, '*.cc')
        self.__folderRunner(self.__path, self.__codeansicfiles, '*.c')
    
    def __folderRunner(self, path, listfiles, extension):
        """
        Find files of a specified type looking a path and its sub-folders recursively
        
        :param path: absolute path for start the search
        :type path: string
        :param listfiles: list to save the absolute paths of the files found
        :type listfiles: string list
        :param extension: the file extension used for search a type of file
        :type extension: string
        """
        
        # Search files in the path
        files = glob.glob(os.path.join(path, extension))
        if len(files) > 0:
            for fileOne in files:
                listfiles.append(fileOne)
                
        # Search sub-folders in the path
        subfolders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        if len(subfolders) > 0:
            # Creation of the absolute path of each sub-folder
            subfolders = [os.path.join(path, f) for f in subfolders]
            # Execution of the function recursively for each sub-folder found
            for subdir in subfolders:
                if not ("examples" in subdir):
                    if not (".svn" in subdir):
                        self.__folderRunner(subdir, listfiles, extension)
            
    def existsFile(self, name):
        """
        Check the existence of the header in the library
        
        :param name: name of header to search (preferably with .h extension)
        :type name: string
        :returns: true if the header exists, false otherwise
        :rtype: boolean
        """
        
        # If the filename does not have the extension .h, it is added
        if not ".h" in name:
            name += ".h"
        # Search the filename in the list of absolute paths of header files
        for h in self.__headerfiles:
            if os.path.basename(h) == name:
                return True
        return False
                 
    def getPath(self):
        """
        Returns the library absolute path
        
        :returns: library absolute path
        :rtype: string
        """
        return self.__path
        
    def getHeaderFiles(self):
        """
        Returns the list of absolute paths of header files
        
        :returns: list of absolute paths of header files
        :rtype: string list
        """
        return self.__headerfiles
    
    def getCppFiles(self):
        """
        Returns the list of absolute paths of C++ code files
        
        :returns: list of absolute paths of C++ code files
        :rtype: string list
        """
        return self.__codecppfiles
    
    def getCFiles(self):
        """
        Returns the list of absolute paths of ANSI C code files
        
        :returns: list of absolute paths of ANSI C code files
        :rtype: string list
        """
        return self.__codeansicfiles