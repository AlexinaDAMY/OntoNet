##################################################
#           ONTONET NOTE
##################################################

# OntoNet is a master student's internship project. It developped in the Transcriptional Control of Chordate Morphogenesis team, on the Center of Research in Cellular Biology of Montpellier (CRBM) in CNRS. OntoNet goal it's to provide an interfaced and automatized way to manage ontology files, with quality controls.

##################################################

import sys
import os
from os import path
from os import listdir
from tkinter import * 
from tkinter import messagebox
from tkinter.ttk import * 
import subprocess
import csv
from csv import writer


# ---- Global variable to easily take them to main file and called them on ended fouction
editedFilePath=''
editedFileFormat=''
TempFiles=''
selectedProjects=[]
selectedFiles=[]




gitCommand='' #It's the git commit command to use it with subprocess, accorded with user entry by the program


#/// Fountion ti hide the waiting window ///

def hideWaitingWin():
    global workInProgress
    workInProgress.destroy()

    workInProgress=Toplevel()
    workInProgress.title('Work in progress...')
    workInProgress.geometry("300x50")
    workInProgress.protocol("WM_DELETE_WINDOW", doNoting()) #user unable to close this window itself (if he can, show and hide waiting window founction can didn't work and some important founction just stop without error message)
    workInProgress.withdraw()

#/// Permit to didn't close waiting window ///
def doNoting():
    pass



#/// Show a long message to user ///

def showLongMess(message):

    showInst=Toplevel()
    showInst.title("")
    showInst.geometry("700x600")

    #Put error message 

    zone_texte = Text(showInst) #Create space to put it
    zone_texte.pack()

    zone_texte.insert("1.0", message)

    button=Button(showInst, text="Close window", command= lambda: showInst.destroy())
    button.pack(pady=20)
   



#/// Asking one information ///

#def askCommitToUser(winTitle,selectedFiles,selectedProjects,interfacePath,ODKPath):
def askCommitToUser(winTitle,userSelectedFiles,userSelectedProjects,interfacePath,ODKPath,givenEditedFilePath,givenEditedFileFormat,ToolTempFiles,githubUser,gitHub_PassWord):

    global editedFileFormat, editedFilePath, TempFiles, selectedProjects, selectedFiles, workInProgress, gitHub_user,gitHub_passWord
    editedFilePath=givenEditedFilePath
    editedFileFormat=givenEditedFileFormat
    TempFiles=ToolTempFiles
    selectedProjects=userSelectedProjects
    selectedFiles=userSelectedFiles
    gitHub_user=githubUser
    gitHub_passWord=gitHub_PassWord

    #-----  Create the waiting window
    workInProgress=Toplevel()
    workInProgress.title('Work in progress...')
    workInProgress.geometry("300x50")
    workInProgress.protocol("WM_DELETE_WINDOW", doNoting()) #user unable to close this window itself (if he can, show and hide waiting window founction can didn't work and some important founction just stop without error message)
    workInProgress.withdraw()

    askWin=Toplevel()
    askWin.title(winTitle)
    askWin.geometry("700x600")

    global entryCommitName, entryCommitDescr

    if winTitle=='Enter your editing information': 
        
        info1=Label(askWin, text='Please enter a short editing message\n\nExemple : \'Adding NameOfArticleOrExperience informations\'')
        info2=Label(askWin, text='You must add a longest description of your edition here\nIf you want write on next line, use the "\\n" symbol\n\nExemple : \'Description first line content \\n Description second line content\'')

        entryCommitName= Entry(askWin, width=60)
        entryCommitDescr= Entry(askWin, width=200)

        validateButton=Button(askWin, text='Validate', command=lambda:[workInProgress.deiconify(),workInProgress.configure(bg='lightgray'),getEntry(),askWin.destroy(),gitCommit(winTitle,interfacePath,ODKPath)])
       



        info1.pack(pady=20)
        entryCommitName.pack(pady=20)
        info2.pack(pady=20)
        entryCommitDescr.pack(pady=20)
        validateButton.pack()



#/// Permit to update global variables commitMessage and commitDescription to close fastly the askWin window ///

def getEntry() :

    global entryCommitName, entryCommitDescr, commitMessage, commitDescription

    commitMessage=str(entryCommitName.get())
  
    commitDescription=str(entryCommitDescr.get())


#/// Do a git commit on the current repertory, push it and return into tool repertory ///


def gitCommit(winTitle,interfacePath,ODKPath):

    global commitMessage, commitDescription, gitCommand, editedFilePath, editedFileFormat, TempFiles, selectedFiles, selectedProjects, gitHub_user, gitHub_passWord


    if commitDescription=='' and commitMessage!='':
        messagebox.showerror(title='Missing information', message='You can\'t leave empty the commit description')
        askCommitToUser(winTitle,selectedFiles,selectedProjects,interfacePath,ODKPath, editedFilePath, editedFileFormat, TempFiles)
        

    if commitMessage=='':
        if commitDescription!='':
            messagebox.showerror(title='Missing information', message='You can\'t leave empty the commit title')
            askCommitToUser(winTitle,selectedFiles,selectedProjects,interfacePath,ODKPath, editedFilePath, editedFileFormat, TempFiles)
        else:
            messagebox.showerror(title='Missing informations', message='You must enter the commits title and description')
            askCommitToUser(winTitle,selectedFiles,selectedProjects,interfacePath,ODKPath, editedFilePath, editedFileFormat, TempFiles)

    if commitDescription!='' and commitMessage!='':
        print('\nUser commit informations are validate')
        if '\\n' in commitDescription:
            gitCommand='git commit -m \'%s\''%(commitMessage)

            remakeCommitDescription=commitDescription.split('\\n')

            for line in remakeCommitDescription: #Remove space symbols before and after \n symbole using by th user
                if line[0]==' ':
                    line=line[1:]
                if line[-1]==' ':
                    line=line[0:-1]

                gitCommand+=' -m \'%s\''%(line)
            

        else:
            gitCommand='git commit -m \'%s\' -m \'%s\''%(commitMessage,commitDescription)


        print('\nCommand to commit project is saved according to user commit information')

        os.system('git remote add origin https://%s:%s@github.com/%s/%s.git'%(gitHub_user,gitHub_passWord,gitHub_user,selectedProjects[0]))


        addAll=subprocess.run(['git','add','--all'], capture_output=True, text=True)

        if addAll.returncode!=0:
            print('There is a problem wit subprocess [git add --all] command')
            print(addAll)
            messagebox.showerror(title='OntoNet', message='Unable use git command to update. Close OntoNet and retry.')
            hideWaitingWin()
        else:

            robot_qualityCheck(interfacePath,ODKPath,editedFilePath,selectedProjects)



#/// Perform quality controls, filter the errors previously selected by user that are untracked and update the untracked errors (unregistered if not exist) ///

def robot_qualityCheck(interfacePath,ODKPath,editedFilePath,selectedProjects):
    global workInProgress


    print('\n\n//////// START "robot_qualityCheck" command ////////')
    print('\nFile with user editions : ', editedFilePath)


    

#TODO make docstrings for each blocs with "///" symbols
 
##################################################
#           DEVOLOPER NOTE
##################################################
#
#This function generates a lot of CSV files. These are:
# - in ODK/target/Project/src/reports: for each test where there is one or more errors, one CSV file with the error(s)
# - in ODK/target/Project/src/ontology/mainReports: files generated by the function
#       . lastErrorReport.csv: merge of all CSV files in ODK/target/Project/src/reports into one, excluding the errors labeled as not errors by the user (in the context of the ontology) ON all PREVIOUS UPDATES! This is the file the user must use to label errors.
#       . LabelledNotError.csv: lists the errors that are not in the context of the project. If the user wants to unlabel one of these errors, they have to delete the row(s) in the CSV (rare case). If one of these errors does not return on update, it is automatically deleted from this file (see lines...)
#       . Report_ErrorsToFix.csv: lists the true errors in the updated project's file. The user must attempt to fix the Error and Warning levels.
#
#
#The function performs these steps:
# - Makes lastErrorReport.csv
# - [From the second project update : if ODK/target/Project/src/ontology/mainReports/LabelledNotError.csv exist] Deletes in LabelledNotError.csv the labeled errors that do not return in lastErrorReport.csv
# - [From the second project update : if ODK/target/Project/src/ontology/mainReports/LabelledNotError.csv exist] Removes from lastErrorReport.csv the labeled errors in LabelledNotError.csv
# - Asks the user to label the false errors in the project context in the lastErrorReport.csv file
# - Adds to LabelledNotError.csv the errors choose by the user and the others are put into Report_ErrorsToFix.csv file
# - Tells the user to see ODK/target/Project/src/ontology/mainReports/Report_ErrorsToFix.csv and to fix Error and Warning levels
#   
##################################################


# First Update : crated the needed directories and files

    print('\n\nRobot quality tests begin')

    ontologyDir='%s/target/%s/src/ontology'%(ODKPath,selectedProjects[0])

    # Create the reports directories if didn't exist yet (first project's update)

    # Variable to know if one window on OntoNet have been generated to say to the user to verificated the ODK path given because there is one problem with directory creation or file deletion (more details on terminal)
    problem='NO'

    if not path.exists('%s/../reports'%(ontologyDir)):
        os.chdir(ontologyDir)
        reportsDirCreate=subprocess.run(['mkdir', '../reports'], capture_output=True, text=True) 
        if reportsDirCreate.returncode!=0 :
            problem='YES'
            messagebox.showerror(title='Major error', message='Creation of directory \'reports\' fail ! See terminal for more informations')
            print('\n\nYour are in ',os.system(pwd),'Report of the failed command is : ', reportsDirCreate)



    else: # If path existing (one update made before the current), I need to delete any previous existing report
        os.chdir(ontologyDir)
        delete=subprocess.run(['rm','-R','../reports'], capture_output=True, text=True)
        reportsDirCreate=subprocess.run(['mkdir', '../reports'], capture_output=True, text=True)

        if delete.returncode!=0 or reportsDirCreate.returncode!=0 :
            if problem=='YES' :
                if delete.returncode!=0 :
                    print('\n\nReport of the failed command is : ', delete)
                if reportsDirCreate.returncode!=0 :
                    print('\n\nReport of the failed command is : ', reportsDirCreate)
            else :
                problem='YES'
                messagebox.showerror(title='Major error', message='Creation of directory \'reports\' fail ! See terminal for more informations')
                print('\n\nYour are in ',os.system(pwd))
                if delete.returncode!=0 :
                    print('\n\nReport of the failed command is : ', delete)
                if reportsDirCreate.returncode!=0 :
                    print('\n\nReport of the failed command is : ', reportsDirCreate)


            
    if not path.exists('%s/mainReports'%(ontologyDir)):
        os.chdir(ontologyDir)
        mainRepDirCreate=subprocess.run(['mkdir', './mainReports'], capture_output=True, text=True) 
        if mainRepDirCreate.returncode!=0 :
            if problem=='YES' :
                print('\n\nReport of the failed command is : ', mainRepDirCreate)
            else :
                problem='YES'
                messagebox.showerror(title='Major error', message='Creation of directory \'reports\' fail ! See terminal for more informations')
                print('\n\nYour are in ',os.system(pwd),'Report of the failed command is : ', mainRepDirCreate)
                

# If there is no problem with previous directory management (can impact report of errors) : write and execute the robot quality tests

    if problem=='NO' :

        os.chdir('%s/QualityTests'%(interfacePath))
        currentLocation=subprocess.run(['pwd'], capture_output=True, text=True)
        #print('\nCurrent location : ',currentLocation.stdout)
    

        robotVerify=subprocess.run(['robot','verify','--input','%s'%(editedFilePath),'--queries', 'annotation_whitespace-violation.sparql', 'duplicate_definition-violation.sparql', 'duplicate_exact_synonym-violation.sparql', 'duplicate_label_synonym-violation.sparql', 'duplicate_scoped_synonym-violation.sparql', 'equivalent_class_axiom_no_genus-violation.sparql', 'equivalent_pair-violation.sparql', 'illegal_use_of_built_in_vocabulary-violation.sparql', 'invalid_xref-violation.sparql', 'label_formatting-violation.sparql', 'missing_definition-violation.sparql', 'missing_superclass-violation.sparql', 'multiple_definitions-violation.sparql', 'multiple_equivalent_class_definitions-violation.sparql', 'multiple_equivalent_classes-violation.sparql','deprecated_boolean_datatype-violation.sparql', 'deprecated_class_reference-violation.sparql','deprecated_property_reference-violation.sparql','duplicate_label-violation.sparql','missing_label-violation.sparql','missing_ontology_description-violation.sparql','missing_ontology_license-violation.sparql','missing_ontology_title-violation.sparql','misused_obsolete_label-violation.sparql','misused_replaced_by-violation.sparql','multiple_labels-violation.sparql','ODK_dc_properties-violation.sparql','ODK_iri_range-violation.sparql','ODK_label_with_iri_violation.sparql','ODK_multiple_replaced_by-violation.sparql','ODK_owldef_self_reference-violation.sparql', '--output-dir','%s/target/%s/src/reports'%(ODKPath,selectedProjects[0])], capture_output=True, text=True)
    
        print('Robots test are made successfully')

        # if robotVerify.returncode !=0 : Not used here because if one error finded the returncode command is 1
       
    #So on lastReport directory I have for each failed rule one csv with 3 columns : entity, property and value. I use all these files to make lastErrorReport.csv file

#Makes lastErrorReport.csv

        print('\n???? STEP 1 BEGIN : Makes lastErrorReport.csv ????')

        os.chdir(ontologyDir)
        currentLocation=subprocess.run(['pwd'], capture_output=True, text=True)
        #print('\nCurrent location : ',currentLocation.stdout)



        suppress=subprocess.run(['rm', './mainReports/lastErrorReport.csv'], capture_output=True, text=True) 
        #Use touch command permit me to delete the contents of the previous lastErrorReport.csv file
        new=subprocess.run(['touch', './mainReports/lastErrorReport.csv'], capture_output=True, text=True) 


        lastErrorsWFile=open('./mainReports/lastErrorReport.csv','w')
        lastErrorsWWriter=writer(lastErrorsWFile)
        addedHeader=['Level','Type of report','Entity','Property','Value']
        lastErrContent=[] # The list of errors in lastErrors.csv file

        #Define the level of violation / error
        errorLevel=['deprecated_boolean_datatype','deprecated_class_reference','deprecated_property_reference','duplicate_definition','duplicate_label','illegal_use_of_built_in_vocabulary','label_formatting','label_whitespace','missing_label','multiple_definitions','multiple_equivalent_class_definitions','multiple_labels','missing_ontology_description','missing_ontology_license','missing_ontology_title','misused_obsolete_label','misused_replaced_by','ODK_dc_properties','ODK_iri_range','ODK_label_with_iri','ODK_multiple_replaced_by','ODK_owldef_self_reference']
        warnLevel=['annotation_whitespace','duplicate_exact_synonym', 'duplicate_label_synonym','duplicate_scoped_synonym', 'equivalent_class_axiom_no_genus', 'equivalent_pair','invalid_xref','missing_definition','missing_obsolete_label','missing_subset_declaration','missing_synonym_type_declaration','multiple_equivalent_classes']
        infoLevel=['lowercase_definition','missing_superclass']

        
        filesIntoLastReport=os.listdir('../reports')

        lastErrorsWWriter.writerow(addedHeader)

        for file in filesIntoLastReport :

            fileNameElements=file.split('-')
            errorType=fileNameElements[0] #To put on lastErrorReport.csv

            if errorType in errorLevel:
                errorLevel='ERROR' #To put on lastErrorReport.csv
            else :
                if errorType in infoLevel:
                    errorLevel='INFO'
                else:
                    errorLevel='WARNING'
        
            report=open('../reports/%s'%(file),'r')
            reportContain=csv.reader(report,delimiter=',')
            next(reportContain)

            rows=[]
            for row in reportContain:
                rows.append(row)
        
            for row in rows:
                addedLine=[]
                addedLine.append(errorLevel)
                addedLine.append(errorType)
                addedLine.append(row[0])
                addedLine.append(row[1])
                addedLine.append(row[2])
    
                lastErrContent.append(addedLine)

            report.close()


        lastErrorsWWriter.writerows(lastErrContent)

        lastErrorsWFile.close()

        print('\n???? STEP 1 END ????')


#Verify condition - if ODK/target/Project/src/ontology/mainReports/LabelledNotError.csv exist

        if path.exists('./mainReports/LabelledNotError.csv'): # [if ODK/target/Project/src/ontology/mainReports/LabelledNotError.csv exist]


#_______________[From second update] Delete in LabelledNotError.csv the labeled errors that do not return in lastErrorReport.csv

            print('\n???? STEP 2 BEGIN :[From second update] Delete in LabelledNotError.csv the labeled errors that do not return in lastErrorReport.csv ????')

    #Rename the LabelledNotError.csv existing file to read it, after create a LabelledNotError.csv file to update it. At the end of deletion, remove the renamed file

            subprocess.run(['mv','./mainReports/LabelledNotError.csv','./mainReports/PreviousLabelledNotErr.csv'], capture_output=True, text=True)
            subprocess.run(['touch','./mainReports/LabelledNotError.csv'], capture_output=True, text=True)

            labelErrorsWFile=open('./mainReports/LabelledNotError.csv','w')
            labelErrorsWWriter=writer(labelErrorsWFile)
            addedHeader=['Level','Type of report','Entity','Property','Value']
            labelErrorsWWriter.writerow(addedHeader)
            labelErrorsWFile.close()

    #Write into created file LabelledNotError.csv the errors returned into lastErrorReport.csv

            lastErrorsRFile=open('./mainReports/lastErrorReport.csv','r')
            lastErrorsRReader=csv.reader(lastErrorsRFile,delimiter=',')
            lastErrorsR=[]
            for row in lastErrorsRReader:
                lastErrorsR.append(row)
        

            PrevlabelErrRFile=open('./mainReports/PreviousLabelledNotErr.csv','r')
            PrevlabelErrRReader=csv.reader(PrevlabelErrRFile,delimiter=',')
            labelErrorsR=[]
            for row in PrevlabelErrRReader:
                labelErrorsR.append(row)


            labelErrorsWFile=open('./mainReports/LabelledNotError.csv','w')
            labelErrorsWWriter=writer(labelErrorsWFile)
        
            for error in labelErrorsR :
                if error in lastErrorsR : #If error in lastErrorsReport.csv, keeped into labelled errors
                    labelErrorsWWriter.writerow(error)


    

            lastErrorsRFile.close()
            PrevlabelErrRFile.close()
            labelErrorsWFile.close()
            subprocess.run(['rm','./mainReports/PreviousLabelledNotErr.csv'], capture_output=True, text=True) 

            print('\n???? STEP 2 END ????')

#_______________[From the second project update] Removes from lastErrorReport.csv the labeled errors in LabelledNotError.csv

            print('\n???? STEP 3 BEGIN :[From the second project update] Removes from lastErrorReport.csv the labeled errors in LabelledNotError.csv ????')

    #Rename the 'lastErrorReport.csv' existing file  into 'UncleanlastErrReport.csv' to read it, after create a lastErrorReport.csv file to update it. At the end of update, remove UncleanlastErrReport.csv

            subprocess.run(['mv','./mainReports/lastErrorReport.csv','./mainReports/UncleanlastErrReport.csv'], capture_output=True, text=True)
            subprocess.run(['touch','./mainReports/lastErrorReport.csv'], capture_output=True, text=True)

            lastErrorsWFile=open('./mainReports/lastErrorReport.csv','w')
            lastErrorsWWriter=writer(lastErrorsWFile)
            addedHeader=['Level','Type of report','Entity','Property','Value','Status']
            lastErrorsWWriter.writerow(addedHeader)
            lastErrorsWFile.close()

    #Write into created file lastErrorReport.csv the errors not in LabelledNotError.csv (remove robot errors that user selected like to be not error on the project context)

            labelErrorsRFile=open('./mainReports/LabelledNotError.csv','r')
            labelErrorsRReader=csv.reader(labelErrorsRFile,delimiter=',')
            #next(labelErrorsRReader) #To didn't read the first line
            labelErrorsR=[]
            for row in labelErrorsRReader:
                labelErrorsR.append(row)
        

            UncleanLastErrRFile=open('./mainReports/UncleanlastErrReport.csv','r')
            UncleanLastErrRReader=csv.reader(UncleanLastErrRFile,delimiter=',')
            uncleanLastErrorsR=[]
            for row in UncleanLastErrRReader:
                uncleanLastErrorsR.append(row)


            lastErrorsWFile=open('./mainReports/lastErrorReport.csv','w')
            lastErrorsWWriter=writer(lastErrorsWFile)
        
            for error in uncleanLastErrorsR :
                if error not in labelErrorsR : #If error not in LabelledNotError.csv, keeped into lastErrorReport.csv
                    lastErrorsWWriter.writerow(error)


    

            labelErrorsRFile.close()
            UncleanLastErrRFile.close()
            lastErrorsWFile.close()
            subprocess.run(['rm','./mainReports/UncleanlastErrReport.csv'], capture_output=True, text=True)

            print('\n???? STEP 3 END ????')

#Verify condition - else :  create mainReports/LabelledNotError.csv and didn't do the optional steps

        else : # If mainReports/LabelledNotError.csv not exist : created it

            print('\n???? STEP 2 & 3 BEGIN : [From first Update] create mainReports/LabelledNotError.csv ????')
   
            subprocess.run(['touch','./mainReports/LabelledNotError.csv'], capture_output=True, text=True)

            labelErrorsWFile=open('./mainReports/LabelledNotError.csv','w')
            labelErrorsWWriter=writer(labelErrorsWFile)
            addedHeader=['Level','Type of report','Entity','Property','Value']
            labelErrorsWWriter.writerow(addedHeader)
            labelErrorsWFile.close()

            print('\n???? STEP 2 & 3 END ????')

#Asks the user to label the false errors in the project context in the lastErrorReport.csv file

        print('\n???? STEP 4 BEGIN : rewrite last errors to display them to the user ????')


        lastErrorsRFile=open('./mainReports/lastErrorReport.csv','r')
        lastErrorsRReader=csv.reader(lastErrorsRFile,delimiter=',')
        uncleanLastErrToLabel=[]

        for row in lastErrorsRReader:
            uncleanLastErrToLabel.append(row)

        lastErrorsRFile.close()



        lastErrToLabel=['  [.Type of report.]  [.Entity.]  [.Property.]  [.Value.]'] #The uncleanLastErrToLabel but all error value is cut at the 15° symbol : make the last errors to label more readable in interface
        for error in uncleanLastErrToLabel:
        
            cleanedError='' #The error with all information and cuted value


            if len(error)!=0: #If it's 0, we are out of index and the error didn't interest us

                cleanedError+='[.' 
                cleanedError+=error[1]
                cleanedError+='.]   [.'
                cleanedError+=error[2]
                cleanedError+='.]   [.'  #Use [. and .] because some values on user file can contain the [ or ] symbols
                cleanedError+=error[3]
                cleanedError+='.]   [.' 

                value=error[4]
                if len(value)>20:
                    newValue=value[0:19]
                else:
                    newValue=value
                cleanedError+=newValue
                cleanedError+='.]'
                lastErrToLabel.append(cleanedError)
    

        print('\n???? STEP 4 BEGIN : rewrite last errors to display them to the user ????')

        hideWaitingWin()
    
        userToChoiceLabelErr(lastErrToLabel,ontologyDir,interfacePath,ODKPath,uncleanLastErrToLabel)





def userToChoiceLabelErr(lastErrToLabel,ontologyDir,interfacePath,ODKPath,uncleanLastErrToLabel):

    global workInProgress
    
    print('\n\n//////// START "userToChoiceLabelErr" command ////////')

    win=Toplevel()
    win.title("Select errors to untrack")
    win.geometry("1500x500")

    userInstruction=Label(win, text='Choose the errors that are not real error in case of your project\n\n[..] significate an empty value')
    userInstruction.pack(pady=20)

    choiceErr=Listbox(win,selectmode = "multiple") #TODO : Upgrade : if possible always, show the first item
    x=1
    for error in lastErrToLabel:
        choiceErr.insert(x, error)
        x=x+1
    choiceErr.pack(fill=X, padx=25, pady=20)

    validate=Button(win, text="Validate", command= lambda: [selected_errors(choiceErr), win.destroy(),workInProgress.deiconify(), workInProgress.configure(bg='lightgray'),updateErrorsReports(ontologyDir,interfacePath,ODKPath,uncleanLastErrToLabel)])
    validate.pack(pady=30)

    print('\n\n//////// END "userToChoiceLabelErr" command ////////')



def selected_errors(listbox):
    #Use a list of selected errors by user, errors into string format
    global userSelectedErrors
    #Reset the variables
    userSelectedErrors=[]

    #Variable to use it in next function to manage welcomePage existingOnto listbox
    for i in listbox.curselection():
        selectedErr=listbox.get(i)
        userSelectedErrors.append(selectedErr)

    #print('\n------- List of user selected errors : ',userSelectedErrors)
    


def updateErrorsReports(ontologyDir,interfacePath,ODKPath,uncleanLastErrToLabel):

    global userSelectedErrors, workInProgress

    workInProgress.deiconify()

    print('\n\n//////// START "updateErrorsReports" command ////////')

    print('\n???? REWRITE ERRORS LISTS BEGIN ????')




    #userSelectedErrors is a list of strings, must transforme strings into lists to permit to selected only the	Type of report	Entity	Property values
    selectedErrors=[] #Errors selected by user into list form
    for errorstring in userSelectedErrors :
        if type(errorstring) != str :
            errorstring=str(errorstring)

        error=[]

        values=errorstring.split('.]') #eg : values = ['[.duplicate_definition', '   [.http://purl.obolibrary.org/obo/CirobuA_0000566', '   [.http://purl.obolibrary.org/obo/IAO_0000115', '   [.Neurons of the', '']

        for value in values[0:-1]: #Don't want the '' elemnt at the end of th list
            valueEle=value.split('[.') #eg : value = '[duplicate_definition' --> valueEle = ['[.', 'duplicate_definition']
            error.append(valueEle[1])
        selectedErrors.append(error)
    #print('////////////',selectedErrors)
        



    #Define longSelectedErrors
    longSelectedErrors=[]
    
    for error in uncleanLastErrToLabel :

        if len(error)>0:  # uncleanLastErrToLabel contain one empty list
        
            shortError=[]
            shortError.append(error[1])
            shortError.append(error[2])
            shortError.append(error[3])
        
            for select in selectedErrors :

                if shortError == select[0:-1]:  #Case of short selected error [Type of report	Entity	Property] corresponding error in lastErrorReport [Level Type of report	Entity	Property Value] matching with short user selected error. 
                    if select[3]=='':
                        longSelectedErrors.append(error)

                    else :
                       
                        if select[3] in error[4][0:19] : #error[4] it's the value.
                            longSelectedErrors.append(error)
    

    #print('\n[last errors detected labelled like not really error] SHORT format : ',selectedErrors)
    #print('\n [last errors detected labelled like not really error] LONG format : ',longSelectedErrors) #Comment in final code, to debug select error(s) in top 3 of the list
    #print('\n[all last errors detected,unlabelled] LONG format : ',uncleanLastErrToLabel[0:2])

    print('\n???? REWRITE ERRORS LISTS END ????')

# Adds to LabelledNotError.csv the errors choose by the user and the others are put into Report_ErrorsToFix.csv file

    print('\n???? STEP 5 BEGIN : Adds to LabelledNotError.csv the errors choose by the user and the others are put into Report_ErrorsToFix.csv file ????')

    print('\n MAKE NEW Report_ErrorsToFix.csv FILES START')




    if path.exists('./mainReports/Report_ErrorsToFix.csv'):
        subprocess.run(['rm','./mainReports/Report_ErrorsToFix.csv'], capture_output=True, text=True)
    subprocess.run(['touch','./mainReports/Report_ErrorsToFix.csv'], capture_output=True, text=True)


    print('\n MAKE NEW Report_ErrorsToFix.csv FILES END')




    #Write into created files LabelledNotError.csv and Report_ErrorsToFix the errors in lastErrToLabel variable according to it's on userSelectedErrors (variable longSelectedErrors) or not

    #--- Read the labelledErrors file contain 


    labelledErrorsRFile=open('./mainReports/LabelledNotError.csv','r')
    labelledErrorsRReader=csv.reader(labelledErrorsRFile,delimiter=',')
    previousLabelErrContain=[]

    previousLabelErrContain.append(['Level','Type of report','Entity','Property','Value'])

    for row in labelledErrorsRReader:
        if row!=['Level','Type of report','Entity','Property','Value']:
            previousLabelErrContain.append(row)


    labelledErrorsRFile.close()


    #print('Errors selected by user : list form and long format (Value complete) : ', longSelectedErrors)


    #--- Write the files

    labelErrorsWFile=open('./mainReports/LabelledNotError.csv','w')
    labelErrorsWWriter=csv.writer(labelErrorsWFile)      

    fixErrorsWFile=open('./mainReports/Report_ErrorsToFix.csv','w')
    fixErrorsWWriter=csv.writer(fixErrorsWFile)

    # Write previous content on labelled errors file
    for row in previousLabelErrContain :
        labelErrorsWWriter.writerow(row)

    # Add the header to 
    addedHeader=['Level','Type of report','Entity','Property','Value']
    fixErrorsWWriter.writerow(addedHeader)


    # Not Update Project if error to fix = NUP
    cptErrToFix=0 #NUP  
    for error in uncleanLastErrToLabel :
        if error!= ['Level','Type of report','Entity','Property','Value'] : #no treat the header selected by the user

            if error in longSelectedErrors : #If error is labelled like not error in project context
                labelErrorsWWriter.writerow(error)
            else: 
                if len(error)>0 and error!= ['Level','Type of report','Entity','Property','Value'] :  #In case it's really an error
                    fixErrorsWWriter.writerow(error)
                    cptErrToFix=cptErrToFix+1 #NUP 



    labelErrorsWFile.close()
    fixErrorsWFile.close()


    print('\n???? STEP 5 END ????')



    # IF all csv are correctly created and no error on project : #NUP 
    if cptErrToFix == 0:
        editGitProjectWithFileContain(ODKPath,interfacePath)
    


  

    print('\n???? COMMIT ON GIT START ????')

    print('\n\n')

    os.chdir('../..') #I want to move to project/src/ontologyDir to project directory
    currentLocation=subprocess.run(['pwd'], capture_output=True, text=True)
    print('\nCurrent location : ',currentLocation.stdout)
    
    
    addProcess=subprocess.run(['git','add','--all'], capture_output=True, text=True)
    #print('\n\n',addProcess)
    if addProcess.returncode!=0 :
        print('ERROR') 
        messagebox.showerror(tile=None, message='Add on gitHub fail')
        hideWaitingWin()

    else:
        commitProcess=subprocess.run([gitCommand], capture_output=True, text=True, shell=True) #shell=True because I give to subprocess.run a string as command
        #print('\n\n',commitProcess)
        commitProcessStatus=''
        if commitProcess.returncode!=0 :
            if (('nothing to commit' not in commitProcess.stdout) and ('Nothing to commit' not in commitProcess.stdout)):
                print('ERROR')
                messagebox.showerror(title=None, message='Commit on gitHub fail', command=workInProgress.destroy())  #
                commitProcessStatus='NO'
            else:
                commitProcessStatus='YES'
            
        if commitProcessStatus=='YES' or commitProcess.returncode==0 :
            pushingProcess=subprocess.run(['git','push'], capture_output=True, text=True)
            #print('\n\n',pushingProcess)
            pushingProcessStatus=''
            if pushingProcess.returncode!=0 :
                if ('nothing to commit' not in pushingProcess.stdout) and ('Nothing to commit' not in pushingProcess.stdout) and ('Everything up-to-date' not in pushingProcess.stdout) and ('everything up-to-date' not in pushingProcess.stdout):
                    if ('nothing to commit' not in pushingProcess.stderr) and ('Nothing to commit' not in pushingProcess.stderr) and ('Everything up-to-date' not in pushingProcess.stderr) and ('everything up-to-date' not in pushingProcess.stderr):
                        messagebox.showerror(title=None, message='Push on gitHub fail', command=workInProgress.destroy())  # 
                        pushingProcessStatus='NO'

                    else : 
                        messagebox.showinfo(title='Your given file has no changes & not error selected', message='The project update not occur', command=workInProgress.destroy()) 
                        pushingProcessStatus='NO'

                else:
                    messagebox.showinfo(title='Your given file has no changes & not error selected', message='The project update not occur', command=workInProgress.destroy()) 

            if pushingProcessStatus!='NO':

            
                if ('nothing to commit' in pushingProcess.stderr) or ('Nothing to commit' in pushingProcess.stderr) or ('Everything up-to-date' in pushingProcess.stderr) or ('everything up-to-date' in pushingProcess.stderr):
                    messagebox.showinfo(title='Your given file has no changes & not error selected', message='The project update not occur', command=workInProgress.destroy()) 

                else:


                    print('\n???? COMMIT ON GIT END ????') 

                #If git push command successfully makes :


                #NUP 
                    if cptErrToFix==0:

                        showLongMess('Your ontology file pass the quality controls : your editions are commited')
                        workInProgress.destroy()
                    else:
                        showLongMess('Errors selection is recorded\n\nYour ontology file NOT pass the quality controls : the list of errors to fix are on file %s/mainReports/Report_ErrorsToFix.csv\n\nPlease fix them, then update again your project to update the ontology file. If you fix the error, the new Report_ErrorsToFix.csv didn\'t contain it.'%(ontologyDir))
                        
                        
            workInProgress.destroy()





    os.chdir('%s'%(interfacePath))




#/// Replace project editable file with user file and push changes into github ///


def editGitProjectWithFileContain(ODKPath,interfacePath):

    global editedFilePath,editedFileFormat,TempFiles,selectedFiles

    print('\n\nFILE ONTOLOGY UPDATE BEGIN ')



    if editedFileFormat != 'ofn' :
        globalResult= subprocess.run(["robot","convert", "-i", editedFilePath, "-o", "%s/%s.owl"%(TempFiles, selectedProjects[0]), "-vvv"], capture_output=True, text=True) #%s permit to put variable under str
        result=globalResult.stderr

        #TODO : If this tool wil be on a server, here Project.owl file bust be name by Projet-RandomID.owl

        if not path.exists('%s/%s.owl'%(TempFiles, selectedProjects[0])) :
            print('!!!! WARNING !!!!\n The given file conversion into ofn fail. ERROR :\n',result)
            editedFileOFNpath="Not exist"
        else:
            editedFileOFNpath='%s/%s.owl'%(TempFiles, selectedProjects[0])
    else:
        editedFileOFNpath=editedFilePath
 

    if editedFileOFNpath=="Not exist":
        showLongMess('Edit project %s fail because it can\'t be convert into ofn format (please see the terminal error)'%(selectedProjects[0]))
    else:
        print('The given file for project update is successfully converted into OFN on TempFiles directory (to be used to edit the ODK project file)')

        os.system('cp %s %s/target/%s/src/ontology/%s.owl'%(editedFileOFNpath,ODKPath,selectedProjects[0],selectedProjects[0]))

        #Do existing project's editable file replacement by user's file
        os.system('rm %s/target/%s/src/ontology/%s-edit.owl'%(ODKPath,selectedProjects[0],selectedProjects[0]))
        os.system('mv %s/target/%s/src/ontology/%s.owl %s/target/%s/src/ontology/%s-edit.owl'%(ODKPath,selectedProjects[0],selectedProjects[0],ODKPath,selectedProjects[0],selectedProjects[0]))
        #print('    THE PROJECT FILE HAS BEEN REPLACED LOCALLY')

 

    
        
