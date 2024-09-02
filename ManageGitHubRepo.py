##################################################
#           ONTONET NOTE
##################################################

# OntoNet is a master student's internship project. It developped in the Transcriptional Control of Chordate Morphogenesis team, on the Center of Research in Cellular Biology of Montpellier (CRBM) in CNRS. OntoNet goal it's to provide an interfaced and automatized way to manage ontology files, with quality controls.

##################################################

import sys
import os
import subprocess
from os import path
from tkinter import messagebox


#/// Function that permit to return list of repertories in a curl command output ///

def GitInfoRepNames(curlOutput) :
    infos=curlOutput.split(",")
    IDontology=[]

    for info in infos:
        if '\"name\"' in info :
            infoElements=info.split(":")
            IDontology.append(infoElements[1][2:-1])

    return IDontology



#/// Function permit to return a list of all gitHub projects existing one github account ///

def listingGitRepo(githubUser, gitHub_PassWord):  #gitHub_PassWord it's the token generated to work with repositories


    #List the public repertories on the GitHub account
    GitRepoPublic= subprocess.run(["curl", "-u","%s:%s"%(githubUser,gitHub_PassWord), "https://api.github.com/users/%s/repos"%(githubUser)], capture_output=True, text=True)

    OutputPublicRepo=GitRepoPublic.stdout  #The output is a string, I use GitInfoRepNames() to analyse it

    ListPublicGitRepo=GitInfoRepNames(OutputPublicRepo)

    #List the private repertories on the GitHub account
    GitRepoPrivate= subprocess.run(["curl", "-u","%s:%s"%(githubUser,gitHub_PassWord), "https://api.github.com/user/repos?type=private"], capture_output=True, text=True)

    OutputPrivateRepo=GitRepoPrivate.stdout #The output is a string, I use GitInfoRepNames() to analyse it

    ListPrivateGitRepo=GitInfoRepNames(OutputPrivateRepo)

    #Make a list of all repertories that existing
    allGitRepo=ListPublicGitRepo
    allGitRepo+=ListPrivateGitRepo


    return allGitRepo



#/// Function to update local files on ODK repertory according to gitHub projects ///

def updateLocalProjects(ODKPath,githubUser,gitHub_PassWord,allGitProjects):

    print("//// Update local projects ////\n\n")


    for project in allGitProjects:

        if not path.exists('%s/target/%s'%(ODKPath,project)) :
            print('\n    ',project,' CLONING')
            print('!!!!!!!!!!!!!! %s/target/%s'%(ODKPath,project))
            os.chdir('%s/target/'%(ODKPath))

            
            cloneCommand="git clone https://%s:%s@github.com/%s/%s.git"%(githubUser,gitHub_PassWord,githubUser,project)
            #print("Cloning command:", cloneCommand)
    
            os.system(cloneCommand)
    
        else :
            print('\n    ',project, ' PULL')
            os.chdir('%s/target/%s'%(ODKPath,project))
            os.system('git pull origin main')



    # If ODK project not in git project, delete in local
    localProjects=os.listdir('%s/target/'%(ODKPath))

    for localProj in localProjects :
        if localProj not in allGitProjects:
            os.system('rm -R -f %s/target/%s'%(ODKPath,localProj))
            if path.exists('%s%s.yaml'%(ODKPath,localProj)) :
                os.system('rm %s%s.yaml'%(ODKPath,localProj))





#/// Function to delete gitHub project(s) on gitHub and locally ///

def deleteAnExistingProject(ODKPath,githubUser,gitHub_PassWord,allUserSelectedProjects, existingOnto,userSelect,IDontology):


    print("//// Delete project(s) : ManageGitHubRepo.py file founction ////\n\n")

    for project in allUserSelectedProjects:
        print('\n Deleting %s'%(project))


        DelCommand=subprocess.run(['curl', "-u","%s:%s"%(githubUser,gitHub_PassWord),'-L','-X','DELETE','-H','\'Accept: application/vnd.github+json\'','-H','\'X-GitHub-Api-Version: 2022-11-28\'','https://api.github.com/repos/%s/%s'%(githubUser,project)], capture_output=True, text=True)


  

    deletion=True
    IDontology=listingGitRepo(githubUser,gitHub_PassWord)  # List of existing projects, using to fill the mainpage listbox updated after project deletion
    for project in allUserSelectedProjects:
        if project in IDontology :
            deletion=False

        
    if deletion==False:
        messagebox.showerror(title=None,message='WARNING : Project deletion fail on GitHub !')

    else:
        os.system('rm -R -f %s/target/%s'%(ODKPath,project))
        if path.exists('%s%s.yaml'%(ODKPath,project)) :
            os.system('rm %s%s.yaml'%(ODKPath,project))
        messagebox.showinfo(title=None,message='Project(s) succesfully deleted')


        for item in userSelect[::-1]: #Set [::-1] to update the item index from existingOnto after each deletion
            existingOnto.delete(item)
            existingOnto.configure(background="white")
       

    

