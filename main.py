##################################################
#           ONTONET NOTE
##################################################

# OntoNet is a master student's internship project. It developped in the Transcriptional Control of Chordate Morphogenesis team, on the Center of Research in Cellular Biology of Montpellier (CRBM) in CNRS. OntoNet goal it's to provide an interfaced and automatized way to manage ontology files, with quality controls.

##################################################

from tkinter import * 
from tkinter.ttk import * 
from tkinter import filedialog # For the browseFile function

import sys
import os
from os import path
import string, re
import subprocess

# My own imported funtions, in other files for more readable code
from ManageProjectCreation import entryFileControl_validateProfil
from ManageProjectCreation import entryFileControl_reason
from ManageProjectCreation import convertImportedFile
from ManageProjectCreation import createYAML
from ManageProjectCreation import createODKRepo

from ManageGitHubRepo import listingGitRepo
from ManageGitHubRepo import updateLocalProjects
from ManageGitHubRepo import deleteAnExistingProject

from EditExistingProject import askCommitToUser


from OBOtreatment import OBO_CLEANING

from tkinter import messagebox
import tkinter.filedialog

#--------------------
# Obtain path to Interface directory
#--------------------

pwdRes=subprocess.run(['pwd'], capture_output=True, text=True) 
interfacePath=pwdRes.stdout[0:-1]




#--------------------
# Variable to change by the user
#--------------------

ODKPath='/home/adamy/Documents/ODK/'


# IMPORTANT : Not founctional now but can be used to improve OntoNet #TODO
#Variable to change the first opened directory in window to choose a file
#For exemple you can put your documents directory : replace next line by " openDirChoseInputFile='home/YourUserName/Documents/' "
openDirChoseInputFile=interfacePath
#openDirChoseInputFile="home/adamy/Documents"

#Variable to change the first opened directory in window to choose an output location (of a cleaned file or when your want convert the format of a file)
#For exemple you can put your working directory : replace next line by " openDirChoseInputFile='Path/To/Your/Working/directory/' "
openDirChoseOutputDir=interfacePath




#--------------------
# Some variable that can change by developper
#--------------------



toolName="OntoNet"
defaultWindowsSizes="1500x700"

RepoForTempFiles="%s/TempFiles"%(interfacePath)

#____global variables, values are set after user clic on button
#List of selected projects
selectedProjects=[]
#List of editable files path for selected projects
selectedFiles=[]

userFile='' #OBO file given by user to be cleaned


#new project informations - permit to put ontology title and description on the project file
projectInfo_ID=""
projectInfo_descr=""

#____Git HUB informations
githubUser= 'AscidiesTeam'
passwordFile=open("./token.txt")
gitHub_PassWord=passwordFile.read()
passwordFile.close()
gitHub_PassWord = gitHub_PassWord.rstrip('\n')

#____The buttons's names
#--------- welcomePage's buttons
buttontitle1="Create a new project"
buttontitle16="Delete project(s)"  
buttontitle2="Update a project"
buttontitle3="Project's editing history"
#--------- TOOLBARE's buttons
buttontitle4="Functions"
buttontitle5="Compare/Align ontologies"
buttontitle6="Convert ontology format"
buttontitle7="Extract one part of ontology"
buttontitle13="Merge ontologies"
buttontitle8="Graphical view"
buttontitle14="Duplicate ontology's part"
buttontitle15="Cleaning OBO file"
#
buttontitle9="Help"

#___For File conversion founction
FileConvert='' #The user file to convert
OutputLocation='' #The user directory where the converted  or obo cleaned file must be saved
#The format the user want to convert a file
OutputFormat=''
InputFormat='' #The format of file given by the user


#___Some tkInter windows can't are global variable because define them automatically showing them





#--------------------------------------------------------------------------
#                                    Some function
#---------------------------------------------------------------------------



#____________________ Temporary founction  


#/// Function for buttons that didn't work right now but should working later  ///

def todoCallBack(buttontitle):
    newWindowTODO=Toplevel(welcomePage)
    newWindowTODO.title(buttontitle)
    newWindowTODO.geometry("300x300")
    Label(newWindowTODO, text="That didn't work now (latter)").pack()


#____________________ Founctional founctions

def browseDir():

    global OutputLocation, openDirChoseOutputDir
    os.chdir(openDirChoseOutputDir)
    OutputLocation=tkinter.filedialog.askdirectory()

#/// Permit to user to select one file ///

def browseFile(extension): 

    global FileConvert, userFile, openDirChoseInputFile
    # f_type = variable to display only right file format to the user
    # Not case of extension==NONE because the function never called in this case
    if extension=="obo":
        f_type=(("OBO files", "*.obo"),)
        filePath=filedialog.askopenfilename(initialdir=openDirChoseInputFile, title="File to import", filetypes=f_type)
    if extension=="obo - cleaning":
        f_type=(("OBO files", "*.obo"),)
        filePath=filedialog.askopenfilename(initialdir=openDirChoseInputFile, title="File to import", filetypes=f_type)
    if extension=="webprotege":
        f_type=(("Webprotege files", "*.ofn"),)
        filePath=filedialog.askopenfilename(initialdir=openDirChoseInputFile, title="File to import", filetypes=f_type)
    if extension=="owl":
        f_type=(("OWL files", "*.owl"),)
        filePath=filedialog.askopenfilename(initialdir=openDirChoseInputFile, title="File to import", filetypes=f_type)
    if extension=="all" or extension=="conversion":
        #f_type=(("All files", "*.*"),) #Don't work on mac


    
        filePath=filedialog.askopenfilename(initialdir=openDirChoseInputFile, title="File to import") #Try to didn't make filetype to Delphine can selected file on MAC

    if extension=="conversion":
        FileConvert=filePath

    if extension=="obo - cleaning":
        userFile=filePath


    return filePath


#/// Do automatical task when user close the tool ///

def onClosing():
    #First delete temporary files generated on the curent session, permit to improve OntoNet  #TODO
    os.system('rm %s/*+' % RepoForTempFiles)




#/// Choose project(s) on existing projects ///

def selected_item(listbox,task):
    #Make a list of selected files
    global selectedFiles, selectedProjects, ODKPath, githubUser, gitHub_PassWord, existingOnto
    #Reset the variables
    selectedProjects=[]
    selectedFiles=[]

    #Variable to use it in next function to manage welcomePage existingOnto listbox
    userSelect=listbox.curselection()

    for i in listbox.curselection():
        selectedFileID=listbox.get(i)
        selectedProjects.append(selectedFileID)
        editableFilePath='%s/target/%s/src/ontology/%s-edit.owl'%(ODKPath,selectedFileID,selectedFileID) #Path to ODK repertory file to edit
        selectedFiles.append(editableFilePath)

    check="OK"

    if task=="qualityControl" or task=='Edit one project' : # I can add some task label where user must select only one project

        #selectProject return a list, I want user select only one project in this case
        if len(selectedFiles)!=1:
            messagebox.showinfo(title=None, message="Only one file is allowed !")
            check="NO"

    #I return nothing because selectedProjects and selectedFiles are global variable

    if task=='Edit one project':
        chooseFile()

    if task=='Delete projects':
        userconfirm(userSelect,selectedProjects)




#/// Show to the user in a new window the error printed by one command  on the terminal ///


def showTerminalError(warning,AcessErrorMessage,messageInFile):
    showWarningWin=Toplevel(welcomePage)
    showWarningWin.title("There is a problem")
    showWarningWin.geometry("700x600")

    warning1=Label(showWarningWin, text=warning)
    warning1.pack(pady=20)

    #Put error message saved in text file

    zone_texte = Text(showWarningWin) #Create space to put it
    zone_texte.pack()

    if messageInFile=="Yes" :
        with open(AcessErrorMessage, "r") as fichier:
            contenu = fichier.read()
            zone_texte.insert("1.0", contenu)
    else:
        if messageInFile=="No" : #In this case the error message is contain on the variable 'AcessErrorMessage'
            zone_texte.insert("1.0", AcessErrorMessage)

    
    instruction1=Label(showWarningWin, text="Please open the given file with a text editor and correct it,make the changes\n and retry to create the project with changed file")
    instruction1.pack(pady=20)

#/// Show a messagebox and close it automatically after a certain time ///


def showMessage(message,typeMessage,timeout,aspect):

    global interfacePath


    MessageWin=Toplevel()
    MessageWin.title(typeMessage)
    MessageWin.geometry("600x250")

    printMess=Label(MessageWin, text=message)
    printMess.pack(pady=20)




    MessageWin.after(timeout, lambda:MessageWin.destroy())



#/// Show a long message to user ///

def showLongInstructions(message,size):

    showInst=Toplevel(welcomePage)
    showInst.title("")
    showInst.geometry(size)
 

    zone_texte = Text(showInst) #Create space to put it
    zone_texte.pack()

    zone_texte.insert("1.0", message)

    
    button=Button(showInst, text="Close window", command= lambda: showInst.destroy())
    button.pack(pady=20)



#/// Show a really long message to user ///

def BIGshowLongInstructions(message):

    showInst=Toplevel(welcomePage)
    showInst.title("")
    showInst.geometry("1400x700")

    zone_texte = Text(showInst, width = 700, height=400, padx=20,pady=20) #Create space to put it
    zone_texte.pack()

    zone_texte.insert("1.0", message)

    
    button=Button(showInst, text="Close window", command= lambda: showInst.destroy())
    button.pack(pady=20)





        






#--------------------------------------------------------------------
#                    New project (ODK repertory) function
#--------------------------------------------------------------------



#/// Windows to ask if user want input a file and if yes the extension ///

def newOntoWindow():

    print('\n\n------------------------------------------\n   CREATION OF A NEW PROJECT STARTING\n------------------------------------------')

    creationOntoWin=Toplevel(welcomePage)
    creationOntoWin.title("How do you want proceed ?")
    creationOntoWin.geometry("650x340")


    # weight=1 permit to extend the grid's column on blank space
    creationOntoWin.grid_columnconfigure(0, weight=1)
    creationOntoWin.grid_rowconfigure(0, pad=20, weight=1)
    creationOntoWin.grid_rowconfigure(1, weight=1) #Not pad here to didn't add it to upper button space (pad)
    creationOntoWin.grid_rowconfigure(2, pad=20, weight=1)
    creationOntoWin.grid_rowconfigure(3, weight=1) #Not pad here to didn't add it to upper button space (pad)

    ButtonNew1=Button(creationOntoWin, text="Import an OBO file", command= lambda: [creationOntoWin.destroy(),newProject("obo")]) 
    ButtonNew2=Button(creationOntoWin, text="Import an OWL file", command= lambda: [creationOntoWin.destroy(),newProject("owl"),])
    ButtonNew3=Button(creationOntoWin, text="Import WebProtege file : ofn format", command= lambda: [creationOntoWin.destroy(),newProject("webprotege")])
    ButtonNew1.grid(column=0, row=0, ipady=10, sticky=W+E)
    ButtonNew2.grid(column=0, row=1, ipady=10, sticky=W+E)
    ButtonNew3.grid(column=0, row=2, ipady=10, sticky=W+E)
 



#/// Asking input file path to the user and try to convert it in OWL format ///

def newProject(importedFileExtension):

    passing=0
    givenPath=browseFile(importedFileExtension) #To have the path to the given file
    if givenPath=='' or givenPath=='()' or len(givenPath)==0:
        messagebox.showerror(title=None, message='Your selection is empty !')
        givenPath=browseFile(importedFileExtension)
    else:

        workInProgress.deiconify()
        removeBlackFrame()

        #Define File's name
        elementsFilePath=givenPath.split("/")
        lastElement=elementsFilePath[-1]
        split=lastElement.split(".") #To split filename to extension(s)
        fileName= split[0]
    
        #Converting the given file into OWL if it's not
        conversion,errorFile,convertedFilePath,jobID=convertImportedFile(importedFileExtension,givenPath,fileName,RepoForTempFiles)   #jobID variable permit to have the same random ID for one generated OWL and it's validation files


        if conversion == "No conversion" : #Given file = owl so didn't convert the given file
            preQualityTest(convertedFilePath,fileName,importedFileExtension,jobID)

        if conversion == "NO" : # The file conversion failed
            convertionMessageErrorInFile="Yes"
            hideWaitingWin()
            showTerminalError("The file can't be read so conversion into OWL fail !",errorFile,convertionMessageErrorInFile)


        if conversion =="YES" : #The given file has been succesfully converted into owl
            filePathEle=convertedFilePath.split('/')
            fileNameEle=filePathEle[-1].split('.')
            fileName=fileNameEle[0]
            preQualityTest(convertedFilePath,fileName,importedFileExtension,jobID)




#/// Do the quality tests : verify the OWL syntaxe and the file's logic ///


def preQualityTest(convertedFilePath,fileName,importedFileExtension,jobID):

    testsInfoWin=Toplevel(welcomePage)
    testsInfoWin.title("Testing the OWL file obteined with your input")
    testsInfoWin.geometry("700x400")

    test1=Label(testsInfoWin, text="Test 1/2 - OWL syntaxe checking")
    test1.pack(pady=20)

    fileStatus1,MessageFilePath=entryFileControl_validateProfil(fileName,RepoForTempFiles,jobID)
    test1MessageInFile="No"

    if fileStatus1=="Fail":
        print("Test 1/2 - profil (OWL DL syntaxe) checking : file didn't pass !\nSee ",MessageFilePath)
        test1MessageInFile="Yes"
        showTerminalError("File converted into OWL - Test 1/2 OWL syntaxe checking",MessageFilePath,test1MessageInFile)
        resTest1=Label(testsInfoWin, text='%s, error recorded on\n%s'%(fileStatus1,MessageFilePath))



    if fileStatus1=="Pass":

        print("Test 1/2 - profil checking : file pass")
        resTest1=Label(testsInfoWin, text=fileStatus1)


    resTest1.pack(pady=20)

    test2=Label(testsInfoWin, text="Test 2/2 - sementic checking")
    test2.pack(pady=20)


    StatusTest2,message=entryFileControl_reason(fileName, RepoForTempFiles,jobID)
    test2MessageInFile="No"
    hideWaitingWin()


    print("Test 2/2 - sementic checking")

    if StatusTest2=="Fail":
        print("Test 2/2 - sementic checking : file didn't pass !")
        showTerminalError("File converted into OWL - Test 2/2 OWL sementic",message,test2MessageInFile)  
        resTest2=Label(testsInfoWin, text=StatusTest2)
        resTest2.pack(pady=20)

    if StatusTest2=="Pass":
        print("Test 2/2 - sementic checking : file pass")
        resTest2=Label(testsInfoWin, text=StatusTest2)
        
    resTest2.pack(pady=20)
        



    if fileStatus1=="Pass" and StatusTest2=="Pass":
        testsInfoWin.destroy()
  

        #Automatically close the message box after 3 seconds
        showMessage('Your file have the correct syntax\nand is empty of reasoning errors','info',3000,'validation')

        ask_project_info(fileName,convertedFilePath)



    else:
        button=Button(testsInfoWin,text="Continue the projet creation", command= lambda: ask_project_info(fileName,convertedFilePath))
        button.pack(pady=20)





#/// Permit to user to write tho project ID and description ///


def ask_project_info(fileName,convertedFilePath):
    global entry1, entry2

    askInfoWin=Toplevel(welcomePage)
    askInfoWin.title("Enter project's informations")
    askInfoWin.geometry("650x340")

    info1=Label(askInfoWin, text='Your project ID (no space / letter and numbers and "-" and "_" only) [ Example : Cirobu_2 ]')
    info1.pack(pady=20)

    entry1= Entry(askInfoWin, width=30)
    entry1.pack()

    info2=Label(askInfoWin, text="Your project short description")
    info2.pack(pady=20)


    entry2= Entry(askInfoWin, width=200)
    entry2.pack()

    ButtonNewProjInfo=Button(askInfoWin, text="Validate informations", command=lambda: [checkInfoNewProj(fileName,convertedFilePath), askInfoWin.destroy()])
 
    ButtonNewProjInfo.pack(pady=20)



#/// Verify if the project ID and description have the requierements, if yes created the repertories ///


def checkInfoNewProj(fileName,convertedFilePath):

    allowedChars=string.ascii_letters+string.digits+'_-'
    allowedSet=set(allowedChars)

    global projectInfo_ID, projectInfo_descr, entry1, entry2, interfacePath, IDontology, existingOnto, welcomePage

    projectInfo_ID=str(entry1.get())
    projectInfo_descr=str(entry2.get())

    #Verify input string are correct
    control="Pass"

    projectInfo_ID_elements=projectInfo_ID.split(" ")
    projectInfo_descr_elements=projectInfo_descr.split(" ")



    if len(projectInfo_ID_elements)==0 or len(projectInfo_descr_elements)==0:
        control="Not pass"
        messagebox.showerror(title=None, message="Project need these information to be created !")  

    if len(projectInfo_ID_elements)>1:
        control="Not pass"
        messagebox.showerror(title=None, message="Space are not allowed on project's ID !")    

    if projectInfo_ID in IDontology:
        messagebox.showerror(title=None, message="An existing project have already this name ! Please change your project ID or use the existing project") 

    if not set(projectInfo_ID).issubset(allowedSet): #set() do list of different characters in variable, and .issubset is true if ALL characters in the set are on allowSet
        control="Not pass"
        messagebox.showerror(title=None, message='Only letters, numbers and "-" or "_" symbols are allowed !')


    if control=="Pass":
        workInProgress.deiconify()
        removeBlackFrame()
        YAMLpath=createYAML(projectInfo_ID,projectInfo_descr,githubUser,interfacePath) #projectInfo_Id and projectInfo_descr are given by the user
        createODKRepo(projectInfo_ID,githubUser,gitHub_PassWord,projectInfo_descr,interfacePath,fileName,convertedFilePath)
        
        #The new id ontology liste that crate the listbow where user select project to delete is on alphabetical order and listbox on main page not : wrong project disapear on main page if project is deleted just after it creation
        newIDontology=[projectInfo_ID]
        for ID in IDontology:
            newIDontology.append(ID)

        IDontology=newIDontology

        hideWaitingWin()

        existIDontology=listingGitRepo(githubUser,gitHub_PassWord)
        if projectInfo_ID not in existIDontology :
            messagebox.showerror(title=None, message='The project creation fail !')
        else:
            showLongInstructions('In order to view the potential logical errors in your created project, please edit it with file using for project creation.\n\nBe bold : at anytime you can use the current version of project\'s ontology file to edit it : that permit you to see the existing errors and select the error to untrack in your project context.\nIn this case if you untrack nothing the projet don\'t change.',"700x600")
            messagebox.showinfo(title=None, message='The project was successfuly created')
            existingOnto.insert(0, projectInfo_ID)


        #Recreated project option window
        welcomePage.update()


        os.chdir('%s'%(interfacePath)) #On createODKRepo() chdir used to move on ODKrepo to connect repertory with GitHub ==> I want to return on interface path after to a potentially next function

    #User need to give project informations again
    else:
        ask_project_info(fileName,convertedFilePath) 












#--------------------------------------------------------------------
#                    Update Project function
#--------------------------------------------------------------------



#/// Window to user edit one existing project : he choose a modified file to replace contain of editable project file by this (gitHub show differrence before and after replacement) ///

def editOntoWindow():


    print('\n\n------------------------------------------\n   EDIT ONE EXISTING PROJECT STARTING\n------------------------------------------')

    global selectedProjects, existingOnto, IDontology

    editing=Toplevel(welcomePage)
    editing.title("Choose one project to edit")
    editing.geometry("650x270")
    

    choiceOnto=Listbox(editing)
    x=1
    for value in IDontology:
        choiceOnto.insert(x, value)
        x=x+1
    choiceOnto.pack(fill=X, padx=25, pady=20)




    validateButton=Button(editing,text='Validate the selection',command=lambda:[selected_item(choiceOnto,'Edit one project'),editing.destroy()]) #Use lambda as list to execute these two commands (editing window it's a local variable)

    validateButton.pack()
    
def chooseFile():

    messageWin=Toplevel(welcomePage)
    messageWin.title('You must selected the ontology edited file')
    messageWin.geometry("650x150")


    #--Label to show to the user the projects selected
    #Construct string with selected projetcs
    message='You selected this project : '
    message+=selectedProjects[0]
    #Construct the label
    messagePrinted=Label(messageWin, text=message)
    messagePrinted.pack(pady=20)

    #--Button 'chose the file to use for the project update / the updated file'
    buttonChoiceFile=Button(messageWin, text='Select the file with changes on your computer\nWARNING : your file must be .owl, .obo or .ofn format', command=lambda: [checkGivenFile(),messageWin.destroy()])
    buttonChoiceFile.pack()





#/// Verify if user give the right file format and the given file URL compared to existing ontology URL ///

def checkGivenFile():
    
    global selectedProjects, selectedFiles, RepoForTempFiles, ODKPath

    givenFilePath= browseFile('all')

    #Read the path to classe into obo, owl or ofn
    giventFilePathElement=givenFilePath.split('.')
    ProjectID=giventFilePathElement[0]
    fileFormat=giventFilePathElement[-1]

    #If not : error message to tell we want one of this format with the extension on file's name and the format of file name
    if fileFormat!='obo' and fileFormat!='ofn' and fileFormat!='owl' and fileFormat!='OBO' and fileFormat!='OFN' and fileFormat!='OWL':
        errorFormatMessage=messagebox.showerror(title=None, message='The selected must be owl, obo or ofn format. It must be name with extension\n[Exemples: \'ProjectName.obo\' or \'ProjectName.OBO\']')

    #I find the two ontology URLs
    else:
        print('The file format is OK :)')

        #print(selectedFiles[0],'\n',givenFilePath)

        if fileFormat == 'obo' or fileFormat == 'OBO' :

            OBOgivenFileConvert=os.system('robot convert -i %s -o %s/%s.owl'%(givenFilePath, RepoForTempFiles,ProjectID)) #Without options, os.system return the command exit code. O mean the command working

    

            if OBOgivenFileConvert != 0:
                print('The OBO input file conversion into OWL fail. Mostly due to OBO syntax error, but keep in mind the used command is os.system() and subprocess.run() can avoid the error')
                messagebox.showerror(title='Your OBO file contain syntax error(s)', message="Your file can't be read correctly. Please correct it before using it to update your project. To see error(s), try to make a new project with your file, correct the error in your file, delete this created project and then retry to update.") 
                OBOfileSyntax='NOT PASS'

            else:
                givenFilePath='%s/%s.owl'%(RepoForTempFiles,ProjectID)
                OBOfileSyntax='PASS'



        if (fileFormat!='obo' and fileFormat!='OBO') or OBOfileSyntax=='PASS':

        
            #### DEV NOTE ####
            #### The correct way to find the ontologyURL it's to use grep command to find the line with the ontology URL and after extract to this line the URL.
            #### The problem is :
            #### - Using grep with os.system() can't return the shell output
            #### - Using grep with subprocess.run() ou .chek_output() return errors
            #### Following commands are try :
            #ontoURLprojectFile=os.system('grep \'Ontology(<http\' %s'%(selectedFiles[0]))
            #ontoURLprojectFile= subprocess.run(["grep", "\'Ontology(<http\'","%s"%(selectedFiles[0])], capture_output=True, text=True)
            #ontoURLprojectFile= subprocess.run(['grep', '\'Ontology(<http\'','%s'%(selectedFiles[0])], shell=True, stdout=subprocess.PIPE)
            #ontoURLprojectFile= subprocess.run(['grep', '\'Ontology(<http\'','%s'%(selectedFiles[0])], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #ontoURLprojectFile= subprocess.check_output(['grep', '\'Ontology(<http\'','%s'%(selectedFiles[0])], shell=True)

            #Search the project ontology URL

            #To avoid 'local variable 'URLlineInfo' referenced before assignment'
            URLlineInfo=''
            ontoURLprojectFile=''

            projFile=open(selectedFiles[0],'r')
            projFileInfos=projFile.readlines()
            projFile.close()

            for line in projFileInfos:
                if line[0]!='#' and ('Ontology(<' in line) :
                    URLlineInfo=line
                    break #Many lines in file but only one not commented with the ontology URL, not necessary to read the other lines 

            if len(URLlineInfo)==0:
                print('URL not found in the file')

            else:
                Infos=URLlineInfo.split("<")
                URLprojectFileUncleaned=Infos[1]
                URLprojectFileCleaned=URLprojectFileUncleaned.split(">")
                ontoURLprojectFile=URLprojectFileCleaned[0] #Escape th '>' symbole

            
            #Search the given file ontology URL

            givFile=open(givenFilePath,'r')
            givFileInfos=givFile.readlines()
            givFile.close()


            if fileFormat=='ofn' or fileFormat=='OFN':
                for line in givFileInfos:
                    if line[0]!='#' and ('Ontology(<' in line) :
                        URLlineInfo=line
                        break #Many lines in file but only one not commented with the ontology URL, not necessary to read the other lines 
                
                
                if len(URLlineInfo)==0:
                    print('URL not found in the file')

                else:
                    Infos=URLlineInfo.split("<")
                    URLGivenFileUncleaned=Infos[1]
                    URLGivenFileCleaned=URLGivenFileUncleaned.split(">")
                    ontoURLGivenFile=URLGivenFileCleaned[0] #Escape th '>' symbole


            else: #Given file it's an owl or an obo (converted into owl)
                for line in givFileInfos:
                    if '<owl:Ontology rdf:about' in line :
                        URLlineInfo=line
                        break #Many lines in file but only one for ontology URL

                if len(URLlineInfo)==0:
                    print('URL not found in the file')

                else:
                    Infos=URLlineInfo.split("=")
                    URLGivenFileUncleaned=Infos[1] # Infos like ["http://purl.obolibrary.org/obo/TEMP">]
                    URLGivenFileCleaned=URLGivenFileUncleaned.split("\"")
                    ontoURLGivenFile=URLGivenFileCleaned[1]
                

            #print('\n\nURL IN THE PROJECT FILE',ontoURLprojectFile)
            #print('\n\nURL IN THE GIVEN FILE',ontoURLGivenFile)



            if ontoURLGivenFile!=ontoURLprojectFile:
                changeOntoURLChoice(givenFilePath,fileFormat, ontoURLGivenFile, ontoURLprojectFile)

            else:
                workInProgress.destroy()
                askCommitToUser('Enter your editing information',selectedFiles,selectedProjects,interfacePath,ODKPath,givenFilePath,fileFormat, RepoForTempFiles,githubUser,gitHub_PassWord)

                





#/// If given file's ontology URL it's different of the existing project URL, ask to user he want to change the URL with the edition ///

def changeOntoURLChoice(editedFilePath,editedFileFormat, ontoURLGivenFile, ontoURLprojectFile):
    changeOntoURL=Toplevel(welcomePage)
    changeOntoURL.title("")
    changeOntoURL.geometry("650x250")

    global selectedProjects, selectedFiles, RepoForTempFiles, interfacePath, ODKPath

    message=Label(changeOntoURL, text="The selected file\'s ontology URL [%s]\nit\'s different of the project ontology URL[%s].\nThe project ontology URL must be change ?"%(ontoURLGivenFile,ontoURLprojectFile))
    message.pack(pady=20)

  
    yesButton=Button(changeOntoURL, text='Yes', command=lambda: [askCommitToUser('Enter your editing information',selectedFiles,selectedProjects,interfacePath,ODKPath,givenFilePath,fileFormat, RepoForTempFiles,githubUser,gitHub_PassWord), changeOntoURL.destroy()])
    

    yesButton.pack(pady=20)

    noButton=Button(changeOntoURL, text='No', command=lambda: [userDirections(ontoURLGivenFile, ontoURLprojectFile,editedFilePath,editedFileFormat),changeOntoURL.destroy()])
    noButton.pack(pady=20)




#/// Given direction for user if ontology URL change it's an error ///

def userDirections(ontoURLGivenFile, ontoURLprojectFile,givenFilePath,fileFormat):

    global selectedFiles


#Make DeclProjectURL, the URL used for classe declaration on the project's file
    URLDeclaration=''
    DeclProjectURL=''

    fileProj=open(selectedFiles[0],'r')
    allLinesProj=fileProj.readlines()
    fileProj.close()
    for line in allLinesProj:
        if line[0] != '#' and 'Declaration(Class(' in line :
            URLDeclaration=line
            break

    if len(URLDeclaration)!=0:
        InfosURLDeclaration=URLDeclaration.split('<') #URLDeclaration like Declaration(Class(<http://webprotege.stanford.edu/RCNlNhGQ4a7nMsFOSOEY86S>))
        UncleanedDeclProjectURL=InfosURLDeclaration[1]
        InfosUncleanedProjectURL=UncleanedDeclProjectURL.split(">")
        DeclProjectURL=InfosUncleanedProjectURL[0]
        URLelements=DeclProjectURL.split("/")
        DeclProjectURL=''
        for element in URLelements[0:-1] :
            DeclProjectURL+=element
            DeclProjectURL+="/"

    print('URL PROJECT DECLARATION CLASS: ',DeclProjectURL)


#Make DeclgivenFileURL, the URL used for classe declaration on user's file 
    fileUser=open(givenFilePath,'r')
    allLinesUser=fileUser.readlines()
    fileUser.close()

    if fileFormat=='ofn' or fileFormat=='OFN':
        for line in allLinesUser:
            if line[0] != '#' and 'Declaration(Class(' in line :
                URLDeclaration=line
                break
        InfosURLDeclaration=URLDeclaration.split('<') #URLDeclaration like Declaration(Class(<http://webprotege.stanford.edu/RCNlNhGQ4a7nMsFOSOEY86S>))
        UncleanedDeclgivenFileURL=InfosURLDeclaration[1]
        InfosUncleanedProjectURL=UncleanedDeclgivenFileURL.split(">")
        allDeclgivenFileURL=InfosUncleanedProjectURL[0]

    else: #If given file is an OBO, it's was converted into owl
        for line in allLinesUser:
            if line[0] != '#' and 'owl:Class rdf:about=' in line :
                URLDeclaration=line
                break
        InfosURLDeclaration=URLDeclaration.split('=') #URLDeclaration like  <owl:Class rdf:about="http://webprotege.stanford.edu/RCNlNhGQ4a7nMsFOSOEY86S">
        UncleanedDeclgivenFileURL=InfosURLDeclaration[1]
        InfosUncleanedProjectURL=UncleanedDeclgivenFileURL.split("\"")
        allDeclgivenFileURL=InfosUncleanedProjectURL[1]
            
            
    DeclgivenFileURLEle=allDeclgivenFileURL.split("/")
    DeclgivenFileURL=''
    for element in DeclgivenFileURLEle [0:-1]:
        DeclgivenFileURL+=element
        DeclgivenFileURL+='/'

    print('URL USER DECLARATION CLASS: ',DeclgivenFileURL)


    shortMess='Please open the file located at %s with a text editor.\nReplace all \'%s\' by \'%s\'. Then save the file and retry to edit the project with this file.'%(givenFilePath,ontoURLGivenFile, ontoURLprojectFile)

    longMess='Please open the file located at %s with a text editor.\n\nReplace all \'%s\' by \'%s\'.\nAlso, under your line starting by [owl:Ontology rdf:about=] (in case of OWL format) or starting by [Ontology(<] (in case of OFN format) ; replace all \'%s\' by \'%s\'.\n\nThen save the file and retry to edit the project with this file.'%(givenFilePath,ontoURLGivenFile, ontoURLprojectFile,DeclgivenFileURL,DeclProjectURL)



    if 'webprotege' in ontoURLGivenFile:
        if 'webprotege' in ontoURLprojectFile: #Case given file and project's file have both one URL that contain 'webprotege'
            if DeclgivenFileURL != DeclProjectURL :
                MessToUser=longMess
            else:
                MessToUser=shortMess
        else : #User file URL contain 'webprotege' but not the project file 
            MessToUser=longMess
    else:
        if 'webprotege' in ontoURLprojectFile: #User file URL dont'n contain 'webprotege' but the project file yes
            MessToUser=longMess
        else: #User file URL  and project file URL dont'n contain 'webprotege'
            if DeclgivenFileURL != DeclProjectURL :
                MessToUser=longMess
            else:
                MessToUser=shortMess


    showLongInstructions(MessToUser,"700x600") #Better than messagebox to print a long text









#--------------------------------------------------------------------
#                   Delete Project function
#--------------------------------------------------------------------




def DelOntoChoiceWindow():

    print('\n\n------------------------------------------\n   DELETE PROJECT(s) STARTING\n------------------------------------------')

    global selectedProjects, existingOnto, IDontology

    deleting=Toplevel(welcomePage)
    deleting.title("Choose one project to delete")
    deleting.geometry("650x270")
    

    choiceOnto=Listbox(deleting,selectmode = "multiple")   
    x=1
    for value in IDontology:
        choiceOnto.insert(x, value)
        x=x+1
    choiceOnto.pack(fill=X, padx=25, pady=20)




    validateButton=Button(deleting,text='Validate the selection',command=lambda:[workInProgress.deiconify(),removeBlackFrame(),selected_item(choiceOnto,'Delete projects'), deleting.destroy()]) #Use lambda as list to execute these two commands (editing window it's a local variable)


    validateButton.pack()


def userconfirm(userSelect,selectedProjects):

    global IDontology, existingOnto

    askingWin=Toplevel()
    winTitle=toolName
    winTitle+=''
    askingWin.title(winTitle)
    askingWin.geometry("500x250")

    message1='Really delete definitively the following :'
    message2=''
    for project in selectedProjects:
        message2+=' %s'%(project)
    message2+=' ?'

    infoL1=Label(askingWin, text=message1)
    infoL2=Label(askingWin, text=message2)
    infoL1.pack(pady=25)
    infoL2.pack()

    validate=Button(askingWin, text='Yes !',command=lambda: [askingWin.withdraw(),workInProgress.deiconify(),removeBlackFrame(), update_IDOntoVariable(selectedProjects),deleteAnExistingProject(ODKPath,githubUser,gitHub_PassWord,selectedProjects,existingOnto,userSelect,IDontology),hideWaitingWin() ,askingWin.destroy()])
    validate.pack(pady=25)

    noValidate=Button(askingWin, text='No',command=lambda: [askingWin.withdraw(),DelOntoChoiceWindow(), askingWin.destroy()])
    noValidate.pack()


    
def update_IDOntoVariable(selectedProjects):
    global IDontology

    print('\n\n/////// USER DELETING PROJECTS : ',selectedProjects)
    updatedIDOntology=[]
    for ID in IDontology :
        print('\n######## Previous list Project : element = ',ID)
        if ID not in selectedProjects :
            updatedIDOntology.append(ID)
            print('Updated IDonto append : ',ID)
    
    IDontology=updatedIDOntology










#--------------------------------------------------------------------
#                   Converting file format function
#--------------------------------------------------------------------



def DefineConversion():
    mainWin=Toplevel()
    winTitle=toolName
    winTitle+=' - File Format conversion'
    mainWin.title(winTitle)
    mainWin.geometry("700x700")

    #Define variables with button name, there are update after user choice
    global FileConvert, OutputLocation,OutputFormat  #There are paths !

    FileConvert=''
    OutputLocation=''
    OutputFormat=''



    #Define the window's widgets
    formatLabel=Label(mainWin, text='Select the output file format')
    choiceFormat=Listbox(mainWin)
    choiceFormat.insert(1, 'OBO')  
    choiceFormat.insert(2, 'OWL')
    choiceFormat.insert(3, 'OFN')

    inputFile=Label(mainWin, text='Select an OBO, OWL or OFN file to convert\nFile extension must be on the name')
    inputFileButton=Button(mainWin, text='Click here', command=lambda:[browseFile("conversion"), checkInputFile(), UserinputFile.configure(text=FileConvert)])
    UserinputFile=Label(mainWin, text=FileConvert)


    outputDir=Label(mainWin, text='Select where save converted file')
    outputDirButton=Button(mainWin, text='Click here', command=lambda:[browseDir(), UserOutputDir.configure(text=OutputLocation)])
    UserOutputDir=Label(mainWin,text=FileConvert)

    validate= Button(mainWin, text='Validate', command=lambda:[getUserInfo(choiceFormat),mainWin.destroy(), workInProgress.deiconify(),removeBlackFrame(),CheckConversionInfo()])

    #Using grid to place widget in 2 colums of 3 rows:
    #https://stackoverflow.com/questions/51631105/how-to-position-several-widgets-side-by-side-on-one-line-with-tkinter

    inputFile.grid(column=0, row=1, pady=25, padx=15)
    inputFileButton.grid(column=2,row=1, pady=25, padx=15)
    UserinputFile.grid(column=0, row=2, columnspan=3, pady=25, padx=15)

    outputDir.grid(column=0,row=3, pady=25, padx=15)
    outputDirButton.grid(column=2,row=3, pady=25, padx=15)
    UserOutputDir.grid(column=0, row=4, columnspan=3, pady=25, padx=15)

    formatLabel.grid(column=0,row=5, pady=25, padx=15)
    choiceFormat.grid(column=2, row=5, pady=25, padx=15)

    validate.grid(column=1, row=6, pady=25, padx=15)





    



def checkInputFile() : #File convert it's the file to converted
    global FileConvert, InputFormat

    print(FileConvert)
    if FileConvert=='':
        messagebox.showerror(title='Unexpected given file',message='The path to your file is empty !')

    allowedFormats=["obo","OBO","ofn","OFN","owl","OWL"]
    fileConvertEle=FileConvert.split('/')
    fileName=fileConvertEle[-1]
    fileNameEle=fileName.split(".")

    if len(fileNameEle)<2 :
        messagebox.showerror(title='Unexpected given file',message='File format must be in this name (ex : file.obo)')
        FileConvert='' #To clean the displaying of chossing file
    else :
        print('FileName variable : ',fileName)
        print('SHORT FileName va : ',fileName[-3:])
        if fileName[-3:] not in allowedFormats :
            messagebox.showerror(title='Unexpected given file',message='Format of file to convert must be obo, ofn or owl')
            FileConvert='' #To clean the displaying of chossing file
        else :
            InputFormat=fileName[-3:].upper() 
            print('InputFormat variable : ',InputFormat)

def getUserInfo(listbox): #get the output format the user want
    global OutputFormat

    print('User selection used to make output format : ',listbox.curselection())
    for i in listbox.curselection():
        print(listbox.curselection())
        OutputFormat=listbox.get(i)
    print('-------- output format :',OutputFormat)
    

def CheckConversionInfo():

    global OutputLocation, FileConvert, InputFormat, OutputFormat #FileConvert was checked  previously

    check='ok'
    restartWin='no'

    if FileConvert=='': #case not selected so check if exist not do
        hideWaitingWin()
        messagebox.showerror(title=None,message='You must enter a file to convert !')
        DefineConversion()

    if OutputLocation=='': #case not selected output format
        hideWaitingWin()
        messagebox.showerror(title=None,message='You must choose the format to convert !')
        DefineConversion()

    else:

        if InputFormat==OutputFormat:
            hideWaitingWin()
            messagebox.showerror(title=None,message='You want to converting %s file into same format !'%(InputFormat))
            check='no'
            restartWin='yes'
            if restartWin=='no':
                DefineConversion()

        if OutputLocation=='':
            hideWaitingWin()
            messagebox.showerror(title=None,message='You must indicate an output directory !')
            if restartWin=='no':
                DefineConversion()
        

        else :
            fileConvertEle=FileConvert.split('/')
            fileName=fileConvertEle[-1]
            if path.exists('%s/%s.%s'%(OutputLocation,fileName[0:-4],OutputFormat.lower())):
                hideWaitingWin()
                showLongInstructions('The file %s existing ! Use this file or rename one file and then converting your file to didn\'t lost data.\nIf the existing file it\'s a previous version not used anymore, you can just delete it.'%(OutputLocation),"700x600")            

            else :
                if check=='ok':
                    convertGivenFile()


def convertGivenFile():

    global OutputLocation, FileConvert, InputFormat, OutputFormat

    fileConvertEle=FileConvert.split('/')
    fileName=fileConvertEle[-1]
    fileNameEle=fileName.split(".")
    fileID=''
    for element in fileNameEle[0:-1]:
        fileID+=element

    #Update OutputLocation with fileID and outputFormat

    OutputLocation+='/'
    OutputLocation+=fileID
    OutputLocation+='.'
    OutputLocation+=OutputFormat.lower()
    print('!!!!!!!! ',OutputFormat,OutputLocation)

    #Update file to convert to put format in lowercase

    InputFormat=InputFormat.lower()
    FileConvert=FileConvert[0:-3]
    print(FileConvert)
    FileConvert+=InputFormat
    print('!!!!!!!! ',InputFormat,FileConvert)

    #Do the conversion

    conversion= subprocess.run(["robot","convert", "-i", FileConvert, "-o", OutputLocation], capture_output=True, text=True) #%s permit to put variable under str
    
    if conversion.returncode!=0:
        hideWaitingWin()
        outputEle=(conversion.stdout).split("\n")
        errorMessage=outputEle[0:-2]
        showLongInstructions('The conversion fail !\n\n%s'%(errorMessage),"700x600")
        if path.exists(OutputLocation) : #robot convert make an empty file 
            subprocess.run(['rm',OutputLocation])
        print(conversion)
    else:
        hideWaitingWin()
        messagebox.showinfo(title=None,message='Your file has been sucessfully convert')
        print(conversion)









#--------------------------------------------------------------------
#                   Cleaning OBO function
#--------------------------------------------------------------------





def OBO_cleaning():

    global userFile, OutputLocation
    userFile=''
    OutputLocation=''

    win=Toplevel()
    win.title('%s - Choose file to cleaning'%(toolName))

    #Place win on the parent window (welcomePage) right to not hide pop-up windows 
    x=welcomePage.winfo_rootx()
    y=welcomePage.winfo_rooty()
    move=400
    placement="900x350+%d+%d"%(x,y+move)
    win.geometry(placement)
    #win.config(width=900, height=350)

    inputFile=Button(win, text='Click to choose your file', command=lambda: [browseFile("obo - cleaning"),printInput.configure(text=userFile)]) #browse update the userFile global variable
    printInput=Label(win, text='')
    inputFile.pack(pady=25)
    printInput.pack()

    outputDir=Button(win, text='Click to choose destination of cleaning file', command=lambda: [verifInputDef(), printOutput.configure(text=OutputLocation)]) #browse update the userFile global variable
    printOutput=Label(win, text='')
    outputDir.pack(pady=25)
    printOutput.pack()

    validate=Button(win,text='Validate',command=lambda:[win.withdraw(),doCleaning(),win.destroy()])
    validate.pack(pady=25)


def verifInputDef():
    global userFile

    topWin=Toplevel() #Permit to put message box really on top level
    topWin.withdraw()

    #print('----',userFile, str(userFile))

    if userFile=='' or userFile==None: #user define outputdir before the file to cleaning
        #define a global variable and print 
        messagebox.showerror(title=None,message='You must define the file to cleaning before',parent=topWin)
   
    else:
        browseDir()
        defineOutputPath()
        topWin.destroy()

    

    

def defineOutputPath():
    global OutputLocation, userFile

    topWin=Toplevel()
    topWin.withdraw()

    if not path.exists(OutputLocation): #User can clic to fast and don't see wrong selection
        messagebox.showerror(title=None,message='Your output directory don\'t exist',parent=topWin)

    else:

        givenOutputDir=OutputLocation
        userFile=str(userFile)             #userFile=tuple object
        userFileEle=userFile.split('/')
        userFileName=userFileEle[-1]
        userFileName='CLEANING_%s'%(userFileName)
        outputPath='%s/%s'%(OutputLocation,userFileName)
        OutputLocation=outputPath

        verifExistFile(givenOutputDir,userFileName)
        
        topWin.destroy()

def confirmOverwriting(givenOutputDir,userFileName):
    global OutputLocation

    win=Toplevel()
    win.title('Confirm chosen directory')
    win.geometry("500x270")

    message=Label(win, text='The selected directory already contain a file %s.\n Did you really want overwrite it ? If not, select another output directory,\nmove the existing file or rename your file to cleaning.'%(userFileName))
    message.pack(pady=25)


    yes=Button(win, text='Yes', command=lambda:win.destroy())
    no=Button(win, text='No',command=lambda:[win.withdraw(), resetOutputLocation(),win.destroy()])
    yes.pack(pady=25)
    no.pack(pady=25)



def resetOutputLocation():

    global OutputLocation

    OutputLocation=''

        
def verifExistFile(givenOutputDir,userFileName):
    global OutputLocation

    if path.exists(OutputLocation) :
        confirmOverwriting(givenOutputDir,userFileName)

def doCleaning():
    global OutputLocation, userFile
        

    if OutputLocation=='' or userFile=='' or OutputLocation==None or userFile==None:
        messagebox.showerror(title=None,message='You must enter the file to cleaning and the directory to save the cleaning file')
        OBO_cleaning()
    else:
        print(userFile)
        workInProgress.deiconify()
        removeBlackFrame()
        corrStatus=OBO_CLEANING(userFile,OutputLocation,RepoForTempFiles)
        hideWaitingWin()

        if corrStatus=='No errors':
            showLongInstructions('No errors that OntoNet can correcting are in your OBO file. The file created is the same that your have selected.\n\nTo verify if your file is really empty of errors, you can try to create a new test project on OntoNet with it. If it still contain error(s), you will have a message with the error description.',"700x600")
        
        else:
            messagebox.showinfo(message='Some errors have been corrected in your file')








#--------------------------------------------------------------------
#                   Others Tool's Founction
#--------------------------------------------------------------------

def hideWaitingWin():
    global workInProgress

    workInProgress.destroy()

    workInProgress=Toplevel()
    workInProgress.title('Work in progress...')
    workInProgress.geometry("300x50")
    workInProgress.protocol("WM_DELETE_WINDOW", doNothing()) #user unable to close this window itself (if he can, show and hide waiting window founction can didn't work and some important founction just stop without error message)
    workInProgress.withdraw()


def removeBlackFrame():   # Process permit to give time to the workInProgress window to be displayed
    global workInProgress
    workInProgress.configure(bg='lightgray')

def Update(): #Update local project according to gitHub projects

    global ODKPath,githubUser,gitHub_PassWord,IDontology

    updateLocalProjects(ODKPath,githubUser,gitHub_PassWord,IDontology)  

    welcomePage.deiconify()







def doNothing():
    pass






#--------------------------------------------------------------------
#                             Welcomepage definition
#--------------------------------------------------------------------



welcomePage = Tk() #I define one window




#I define the window title
welcomePageTitle=toolName
welcomePageTitle+=" - Main page"
welcomePage.title(welcomePageTitle)

#I define the window size when this program is started
welcomePage.geometry(defaultWindowsSizes)




#____________________ TOOLBARE

menubar=Menu(welcomePage)

#Functions menu
#Create 'menu1' object, not labelled
menu1 = Menu(menubar, tearoff=0) 

# In first the cleaning OBO file and converting format buttons are here, in the toolbare. They are moved on main page to permit Delphine to use them, but to didn't move OntoNet's toolbare help section, I put two empty button here
menubar.add_command(label='', command= lambda: doNothing()) 
menubar.add_command(label='', command= lambda: doNothing) 


#Help menu
menu2 = Menu(menubar, tearoff=0)
file=open('%s/Help/UseWPandOntoNet_CreateOnto.txt'%(interfacePath),"r")
content=file.readlines()
mess1=''
for line in content:
    mess1+=line
menu2.add_command(label='Create a WebProtege editable project', command= lambda: showLongInstructions(mess1,"700x600"))
file.close()

file=open('%s/Help/gitHubHistory.txt'%(interfacePath),"r")
content=file.readlines()
mess2=''
for line in content:
    mess2+=line
menu2.add_command(label='Access to project\' history', command= lambda: showLongInstructions(mess2,"700x600"))
file.close()

file=open('%s/Help/FileOrganisation.txt'%(interfacePath),"r")
content=file.readlines()
mess3=''
for line in content:
    mess3+=line
menu2.add_command(label='Files organization into your project', command= lambda: showLongInstructions(mess3,"700x600"))
file.close()

#--------------------------------------------------------------

menu2.add_separator()
file=open('%s/Help/HowReadError.txt'%(interfacePath),"r")
content=file.readlines()
mess4=''
for line in content:
    mess4+=line
menu2.add_command(label='Reading OntoNet errors (after ontology quality controls)', command= lambda: showLongInstructions(mess4,"700x600"))
file.close()

file=open('%s/Help/typeErrorsDefinition_ANGL (makein csv).txt'%(interfacePath),"r")
content=file.readlines()
mess5=''
for line in content:
    mess5+=line
menu2.add_command(label='Definition of each errors types', command= lambda: BIGshowLongInstructions(mess5))
file.close()


#--------------------------------------------------------------

menu2.add_separator()
file=open('%s/Help/OntologyFormats.txt'%(interfacePath),"r")
content=file.readlines()
mess6=''
for line in content:
    mess6+=line
menu2.add_command(label='The existing ontology formats', command= lambda: showLongInstructions(mess6,"900x600"))
file.close()



menubar.add_cascade(label=buttontitle9, menu=menu2)

#Become effective this buttons :
welcomePage.config(menu=menubar)




#____________________ OTHERS PAGE'S ELEMENTS


listBoxTitle = Label(welcomePage, text="Locally existing projects (one project = one ontology)")
#pad permit to give external space, around the widget (X and Y)
listBoxTitle.pack(pady=25)




#Create the list of existing anatomical ontologies 
global IDontology
IDontology=listingGitRepo(githubUser,gitHub_PassWord)  



#Printed existing projects on GitHub
existingOnto=Listbox(welcomePage)
x=1
for value in IDontology:
    existingOnto.insert(x, value)
    x=x+1
existingOnto.pack(fill=X, padx=45)
#existingOnto.grid(column=0, row=0, columnspan=4, rowspan=5)

#Create an invisible label, to make space beetween listbox and buttons
#invisibleLabel1=Label(welcomePage, text=" ")
#invisibleLabel1.pack(pady=30)

#Put the buttons on main interface page
B1=Button(welcomePage,text=buttontitle1, command= lambda: newOntoWindow()) #'lambda' permit to activate the commande only when clic on the button https://stackoverflow.com/questions/42099611/activating-function-only-when-tkinter-button-clicked-on-python
B1.place(x=400, y=300)
#B1.pack(pady=15)
#B1.grid(column=1, row=6, ipady=10)

B2=Button(welcomePage,text=buttontitle2, command= lambda: editOntoWindow())
B2.place(x=410, y=400)
#B2.grid(column=1, row=7, ipady=10)


B3=Button(welcomePage,text=buttontitle16, command= lambda: DelOntoChoiceWindow())
B3.place(x=410, y=500)
#B3.grid(column=1, row=8, ipady=10)

B4=Button(welcomePage,text=buttontitle15, command= lambda: OBO_cleaning())
B4.place(x=820, y=300)
#B4.grid(column=2, row=6, ipady=10)

B5=Button(welcomePage,text=buttontitle6, command= lambda: DefineConversion())
B5.place(x=800, y=400)
#B5.grid(column=2, row=7, ipady=10)


welcomePage.withdraw()





#Make the waiting window and hide it
workInProgress=Toplevel()
workInProgress.title('Work in progress...')
workInProgress.geometry("300x50")
workInProgress.protocol("WM_DELETE_WINDOW", doNothing()) #user unable to close this window itself (if he can, show and hide waiting window founction can didn't work and some important founction just stop without error message)
workInProgress.withdraw()


#Make a window to User start the gitHub data dowload
firstWin=Toplevel()
firstWin.title(toolName)
firstWin.geometry("400x80")
startButton = Button(firstWin, text="Update with GitHub datas", command=lambda:[firstWin.destroy(),workInProgress.deiconify(),removeBlackFrame(),Update(),hideWaitingWin()])
#startButton = Button(firstWin, text="Update with git Hub datas", command=lambda:[firstWin.destroy(),showWaitingWin(),workInProgress.update()])
startButton.pack(pady=25)




welcomePage.mainloop()


