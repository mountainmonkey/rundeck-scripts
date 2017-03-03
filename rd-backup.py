#!/usr/bin/python
import json
import requests
import xml.etree.ElementTree as ET

API_KEY=''
RUNDECKSERVER = 'http://127.0.0.1'
RUNDECKPORT='4440'

# API call to get the list of the existing projects on the server.
def listProjects():
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/projects'
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, headers=headers, verify=False)
    return r.text.encode('utf-8')
    
# Returns list of all the project names
def getProjectNames(projectXML):
    project_names = []
    root = ET.fromstring(projectXML)
    for projects in root:	
        for name in projects.findall('project'):
            project_names.append(name.find('name').text)
    return project_names   
    
# API call to get the list of executions of a project.
def exportArchive(projectName):
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/11/project/'+projectName+'/export'
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, headers=headers, verify=False)
    f = file(projectName+".zip","wb")
    f.write(r.content)
    f.close()

projects = getProjectNames(listProjects())
for project in projects:
    print 'project:\t'+project
    exportArchive(project)
