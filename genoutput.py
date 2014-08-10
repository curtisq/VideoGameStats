# -*- coding: utf-8 -*-
#Mostly taken from xhtml22pdf examples

__version__ = "$Revision: 194 $"
__author__  = "$Author: holtwick $"
__date__    = "$Date: 2008-04-18 18:59:53 +0200 (Fr, 18 Apr 2008) $"

import os
import inspect
import sys
import cgi
import cStringIO
import logging

import renderJinjaTemplates
import finaldict

CURRENT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def makeOutput(src="./output/output.html"):
    template = renderJinjaTemplates.loadTemplate(location = "steam/macaw/pagetest/index_template2.html")
    data = finaldict.genDict()
    str = renderJinjaTemplates.renderTemplate(template, data)
    encoded_str = str.encode('utf-8')

    file = open(src, "w")
    file.write(encoded_str)
    file = open("./test.txt", "a")
    file.write("another test...")
    file.close()

if __name__=="__main__":
    spath = CURRENT_PATH + "/output/output.html"
    makeOutput(src=spath)
