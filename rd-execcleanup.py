#!/usr/bin/python
import json
import requests
import sys
import time
import xml.etree.ElementTree as ET

API_KEY='ci75m4XsXQJHIt9e8aghcT6N8fP9DIdj'
RUNDECKSERVER = 'http://127.0.0.1'
RUNDECKPORT='4440'
EXPIRE_DAYS = 30
TODAY = int(round(time.time() * 1000))
#EXPIRE_MILISECONDS = EXPIRE_DAYS * 24 * 60 * 60 * 1000
END_DATE=TODAY-(EXPIRE_DAYS * 24 * 60 * 60 * 1000);
#END_DATE=TODAY;

# API call to get the list of the existing projects on the server.
def listProjects():
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/projects'
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, headers=headers, verify=False)
    return r.text.encode('utf-8')
    
# Returns list of all the project names
def getProjectNames(projectsXML):
    project_names = []
    root = ET.fromstring(projectsXML)
    for projects in root:	
        for name in projects.findall('project'):
            project_names.append(name.find('name').text)
    return project_names   

# API call to get the list of the jobs that exist for a project.
def listJobsForProject(project_name):
    #url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/14/project/'+project_name+'/jobs'
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/jobs'
    payload = { 'project':  project_name }
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, params=payload, headers=headers, verify=False)
    #r = requests.get(url, headers=headers, verify=False)
    return r.text.encode('utf-8')

# Returns list of all the jobids
def getJobIDs(jobsinfo_xml):
    job_ids = []
    root = ET.fromstring(jobsinfo_xml)	
    for jobs in root:
        for job in jobs:
            job_ids.append(job.attrib['id'])
    return job_ids

# API call to get the list of the executions for a Job.      
def getExecutionsForAJob(jobID):
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/job/'+job_id+'/executions'
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, headers=headers, verify=False)
    return r.text.encode('utf-8')

# Returns a dict {'execution_id01': 'execution_date01', 'execution_id02': 'execution_date02', ... }
def getExecutionDate(executionsXML):
    execid_dates = {}
    root = ET.fromstring(executionsXML)
    for executions in root:     
        for execution in executions.findall('execution'):
            execution_id = execution.get('id')
            for date in execution.findall('date-ended'):
                execution_date = date.get('unixtime')
    	    execid_dates[execution_id] = execution_date
    return execid_dates

#API call to delete an execution by ID
def deleteExecution(execution_id):
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/12/execution/'+execution_id
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.delete(url, headers=headers, verify=False)
    print "result: "+r.text

def isOlderThanExpireDays(execution_date, today):
    if ((today - execution_date) > EXPIRE_MILISECONDS):
        return True
    return False

def checkDeletion(execid_dates):
        if isOlderThanExpireDays(int(exec_date), TODAY):
    	    deleteExecution(exec_id)

# API call to get the list of executions of a project.
def listExecsForProject(projectName):
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/14/project/'+projectName+'/executions'
    #args = { 'olderFilter': str(EXPIRE_DAYS)+'d','max':'1' }
    #args = { 'olderFilter': '1y','max':'1' }
    #args = { 'recentFilter': '5h' }
    #args = { 'begin': 0 }
    args = { 'end':str(END_DATE),'max':'900' }
    print "args:"+str(args)
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, params=args, headers=headers, verify=False)
    #print "result:" + r.text.encode('utf-8')
    return r.text.encode('utf-8')

# extract execution id and put them into a list
def getExecIDs(execsXML):
    exec_ids = []
    root = ET.fromstring(execsXML)
    for execution in root.findall('execution'):
    #    print "eid:"+ execution.get('id')
        exec_ids.append(execution.get('id'))
    return exec_ids

#API call to bulk delete
def bulkDeleteExecution(exec_ids):
    if (len(exec_ids) < 1):
        print "no executions to delete in this project!\n"
    else: 
        url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/12/executions/delete'
        headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
        print "deleting executions: " + str(exec_ids)
        r = requests.post(url, headers=headers, data=json.dumps(exec_ids), verify=False)
        print "result: "+r.text

if (len(sys.argv) > 1):
    EXPIRE_DAYS = sys.argv[1]
print "deleteing executions older than "+str(EXPIRE_DAYS)+" days..."

projects = getProjectNames(listProjects())
for project in projects:
    print 'project:\t'+project
    bulkDeleteExecution(getExecIDs(listExecsForProject(project)))
    #ids=getExecIDs(listExecsForProject(project))
    #for exec_id in ids:
    #    print exec_id+","
    #    deleteExecution(exec_id)

    #listJobsForProject(project)
    #jobids = getJobIDs(listJobsForProject(project))
    #print "jobid: "+jobids[0]
    #for jobid in jobids:
    #    print '\tjobid:\t'+jobid
    #    checkDeletion(getExecutionDate(getExecutionsForAJob(jobid))) 
