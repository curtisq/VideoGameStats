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


CURRENT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def Ftemplatedata():
    data = {}
    data['title'] = "Customer Care Report"
    data['head_stylesheets'] = ["../templates/Fcssprint.css"] #for xhtml2pdf
    #data['head_stylesheets'] = ["../templates/Fcss.css"] # for web
    data['body_pages'] = []
    pageA = {
                'headerImage': "../images/ss.png",
                'headerText': "CUSTOMER CARE REPORT",
                'table': {
                    'id': "table1",
                    'title': "VOLUME AND CSAT",
                    'headerRow': ["WEEKENDING", "2014-07-18", "2014-07-11", "CHANGE"],
                    'rows': [
                        {
                            'class': 'row1class',
                            'data': [
                                {'class': 'rowLabel', 'content': "EMAIL CASES PER AAPS"},
                                {'class': 'numdata', 'content': "12,439"},
                                {'class': 'numdata', 'content': "11,962"},
                                {'class': 'numdata', 'content': "4.0%"},
                            ]
                       },

                       {
                           'class': 'row2class',
                           'data': [
                               {'class': 'rowLabel', 'content': "CHAT REQUESTS PER AAPS"},
                               {'class': 'numdata', 'content': "13,139"},
                               {'class': 'numdata', 'content': "12,761"},
                               {'class': 'percdata', 'content': "2.0%"},
                            ]
                        },

                        {
                            'class': 'spaceAfter',
                            'data': [
                                {'class': 'rowLabel', 'content': "INBOUND INTERACTIONS PER CASE"},
                                {'class': 'numdata', 'content': "22,798"},
                                {'class': 'numdata', 'content': "21,784"},
                                {'class': 'percdata', 'content': "4.7%"},
                            ]
                        },

                        {
                           'class': 'row2class',
                           'data': [
                               {'class': 'rowLabel', 'content': "EMAIL CSAT"},
                               {'class': 'numdata', 'content': "0.68"},
                               {'class': 'numdata', 'content': "0.71"},
                               {'class': 'redValue', 'content': "-4.2%"},
                            ]
                        },

                        {
                           'class': 'row2class',
                           'data': [
                               {'class': 'rowLabel', 'content': "CHAT CSAT"},
                               {'class': 'numdata', 'content': "0.68"},
                               {'class': 'numdata', 'content': "0.71"},
                               {'class': 'redValue', 'content': "-4.2%"},
                            ]
                        },
                    ]
                }, #end of table dict
                'charts': {
                    'id': "chart1",
                    'leftChart': "../images/leftchart.png",
                    'rightChart': "../images/rightchart.png",
                },
                'date': "2014-07-28",
                'reportName': "SQUARESPACE CUSTOMER CARE REPORT",
    }
    pageB = {
                'headerImage': "../images/ss.png",
                'headerText': "CUSTOMER CARE REPORT",
                'table': {
                    'id': "table2",
                    'title': "COVERAGE",
                    'headerRow': ["WEEKENDING", "2014-07-18", "2014-07-11", "CHANGE"],
                    'rows': [
                        {
                            'class': 'row1class',
                            'data': [
                                {'class': 'rowLabel', 'content': "TIME TO RESOLUTION"},
                                {'class': 'numdata', 'content': "21"},
                                {'class': 'numdata', 'content': "21"},
                                {'class': 'redValue', 'content': "-0.3%"},
                            ]
                       },

                       {
                           'class': 'row2class',
                           'data': [
                               {'class': 'rowLabel', 'content': "PERCENT CHAT REQUEST REALIZED"},
                               {'class': 'numdata', 'content': "21"},
                               {'class': 'numdata', 'content': "21"},
                               {'class': 'redValue', 'content': "-0.3%"},
                            ]
                        },
                   ]
                }, #end of table dict
                'charts': {
                    'id': "chart1",
                    'leftChart': "../images/rightchart.png",
                    'rightChart': "../images/leftchart.png",
                },
                'date': "2014-07-28",
                'reportName': "SQUARESPACE CUSTOMER CARE REPORT",
    }

    data['body_pages'].append(pageA)
    data['body_pages'].append(pageB)

    return data


def makePDF(src="./templateOutput/Foutput.html", dest="/pipeline/data/reports/genpdf.pdf"):
    template = renderJinjaTemplates.loadTemplate(location = "index_template.html")
    data = {}
    data['header_text'] = "THIS IS TEXT"
    template = renderJinjaTemplates.renderSaveTemplate(template, data, src)
    #check dest exists and is writeable
    if not os.path.exists(os.path.dirname(dest)):
        print dest + " directory for file does not exist"
        return
    if not os.access(os.path.dirname(dest), os.W_OK):
        print dest + " directory for file is not writeable"
        return
    #generatePDFfromFile(src, dest)

if __name__=="__main__":
    spath = CURRENT_PATH + "/output.html"
    makePDF(src=spath)
