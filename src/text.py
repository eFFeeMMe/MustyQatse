#!/usr/bin/env python
import os
from ConfigParser import ConfigParser

#Let there be uglyness
try:
    yet = _firstImport
except NameError:
    _parser = ConfigParser()
    
    _preloadedStrings = {}
    _preloadedSections = {}
finally:
    _firstImport = False

def loadLanguage(language="en-US"):
    filePath = os.path.abspath(os.path.join(os.path.abspath("data"), "languages", language + ".ini"))
    _parser.readfp(open(filePath))

def getString(section, option):
    try:
        sct = _preloadedStrings[section]
    except KeyError:
        sct = _preloadedStrings[section] = {}
    finally:
        try:
            string = sct[option]
        except KeyError:
            string = _parser.get(section, option)
            sct[option] = string
        finally:
            return string

def getSection(section):
    try:
        sct = _preloadedSections[section]
    except KeyError:
        sct = _preloadedSections[section] = tuple(item[1] for item in _parser.items(section))
    finally:
        return sct
