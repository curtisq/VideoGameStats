import jinja2
import os
import inspect


FILE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def loadTemplate(location="template.htmljinja"):
    tpath = FILE_PATH + "/templates/"
    templateLoader = jinja2.FileSystemLoader([tpath, FILE_PATH, "./templates/", "./jinjaTemplates/templates/"])
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(location)
    return template

def renderTemplate(template, data):
    str = template.render(data)
    return str

def renderSaveTemplate(template, data, outfile="./templateOutput/outputhtml.html"):
    str = template.render(data)
    text_file = open(outfile, "w")
    text_file.write(str)
    text_file.close()

if __name__ == "__main__":
    template = loadTemplate()

    info = {}
    info['title'] = "Site title"
    info['text_a'] = "Extra text"
    info['heading_a'] = "This is a H1 element."
    info['head_stylesheets'] = ["csstest.css"]
    
    renderSaveTemplate(template, info)
