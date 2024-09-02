##################################################
#           ONTONET NOTE
##################################################

# OntoNet is a master student's internship project. It developped in the Transcriptional Control of Chordate Morphogenesis team, on the Center of Research in Cellular Biology of Montpellier (CRBM) in CNRS. OntoNet goal it's to provide an interfaced and automatized way to manage ontology files, with quality controls.

##################################################

import sys
import os
import subprocess

#To generate random strings
import random
import string



#--------------------
# Variable to change by the user
#--------------------

ODKPath='/home/adamy/Documents/ODK/'





#------------------------------------------------------------------------------------------
#            FUNCTION TO TRANSFORM GIVEN FILE ON OWL
#------------------------------------------------------------------------------------------


#/// Convert the imported file into a classical OWL file ///

def convertImportedFile(fileFormat, filePath, fileName, RepoForTempFiles):

    i=0
    generatedFileID=''
    for i in range(10):
        newCar=random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        newCar=str(newCar[0])
        generatedFileID+=newCar
        i=i+1

 

    #In first I want convert file into owl if it's an obo or a csv (to run validity tests with ROBOT tool)
    #I need to take the robot's command output to give it to the user
        
    if fileFormat=="obo":
        globalResult= subprocess.run(["robot","convert", "-i", filePath, "-o", "%s/%s.owl"%(RepoForTempFiles, fileName), "-vvv"], capture_output=True, text=True) #%s permit to put variable under str
        result=globalResult.stderr

    if fileFormat=="webprotege":
        globalResult= subprocess.run(["robot","convert", "-i", filePath, "-o", "%s/%s.owl"%(RepoForTempFiles, fileName), "-vvv"], capture_output=True, text=True)
        result=globalResult.stderr

    if fileFormat=="owl":
        os.system("cp %s %s/%s.owl"% (filePath, RepoForTempFiles, fileName))
        conversion="YES"
        ErrorFilePath='NONE'
        convertedFilePath='%s/%s.owl'%(RepoForTempFiles, fileName)

    #Now in each case we have the imported file in owl format in our temporary directory if That's work

    #But if that not working, we want show on interface why

    if fileFormat!="owl":
        if result=="" :
            print("It's ok, no problem to converted given file into OWL")
            conversion="YES"
            ErrorFilePath="NONE"
            convertedFilePath='%s/%s.owl'%(RepoForTempFiles, fileName)

        else:
            file=open('%s/ConversionError_%s_%s.txt'%(RepoForTempFiles,fileName,generatedFileID),'w')
            file.write(result)
            file.close()

            #Filtering error message if user give an obo file (message with all parsers error, just one it's adapted to read OBO format)
            if fileFormat=="obo": #Case file is converted and it's obo format
                    
                print("Filter the error file : %s/ConversionError_%s_%s.txt"%(RepoForTempFiles,fileName,generatedFileID))
                os.system('grep -m 2 -e "^LINENO" -e "^LINE" %s/ConversionError_%s_%s.txt > %s/FilteredConversionError_%s_%s.txt'%(RepoForTempFiles,fileName,generatedFileID,RepoForTempFiles,fileName,generatedFileID))
                    

                ErrorFilePath='%s/FilteredConversionError_%s_%s.txt'%(RepoForTempFiles,fileName,generatedFileID)
                convertedFilePath='None'
                conversion="NO"

           

            ErrorFilePath='%s/FilteredConversionError_%s_%s.txt'%(RepoForTempFiles,fileName,generatedFileID)
            convertedFilePath='None'
            conversion="NO"



    return conversion, ErrorFilePath, convertedFilePath, generatedFileID


#------------------------------------------------------------------------------------------
#            MY TWO QUALITY TEST OF FILE TO CONSTRUCT ONTOLOGY'S FIRST RELEASE
#------------------------------------------------------------------------------------------


#/// Check the OWL syntax ///


def entryFileControl_validateProfil(fileName, RepoForTempFiles, jobID):  #jobID it's the random key generated on input file conversion into OWl, I want generated validation files with this same ID


    os.system("robot validate-profile --profile DL -i %s/%s.owl -o %s/%s-validationProfil-%s.txt" % (RepoForTempFiles, fileName, RepoForTempFiles, fileName, jobID))

    messageFilePath="%s/%s-validationProfil-%s.txt"%(RepoForTempFiles, fileName,jobID)
    
    file=open(messageFilePath,"r") 
    result=file.read()
    file.close()

    message="%s/%s-validation.txt"%(RepoForTempFiles, fileName)
    if "[Ontology and imports closure in profile]" in result :
        RB_test1="Pass"
    else:
        RB_test1="Fail"

    return RB_test1, messageFilePath




#/// Check the semantic ///


def entryFileControl_reason(fileName, RepoForTempFiles, jobID): #jobID it's the random key generated on input file conversion into OWl, I want generated validation files with this same ID



    reasonResult= subprocess.run(["robot", "reason", "-i", "%s/%s.owl"%(RepoForTempFiles, fileName), "-o", "%s/%s-reasoned-%s.owl" % (RepoForTempFiles, fileName,jobID)], capture_output=True, text=True)


    if reasonResult.stdout=="":
        RB_test2="Pass"

    else:
        RB_test2="Fail"

    message=reasonResult.stdout
        
    return RB_test2, message



#------------------------------------------------------------------------------------------
#            FUNCTION TO CREATE YAML FILE - give project informations to ODK in a text file
#------------------------------------------------------------------------------------------

#/// Create the config file according to user informations ///

def createYAML(projectID, description,githubUser,interfacePath):

    global OntoDescr

    #Remove space and other caratère of the description
    blankChar = " \t\n"

    cleaningDescr = "".join(x for x in description if x not in blankChar)

    if cleaningDescr=='' :
        OntoDescr="No description for this project"
    else:
        OntoDescr=description  #The description of ontology is in this file global variable, so need to be updated here if no empty




    file=open("%s/%s.yaml"%(ODKPath, projectID),"w")

    file.write('id: %s\n'%(projectID))
    file.write('title: "%s"\n'%(projectID))
    file.write('description: %s\n'%(description))  #Give ODK's project informations
    file.write('repo: %s\n'%(projectID))
    file.write('license: https://creativecommons.org/licenses/unspecified\n')

    #By default : export formats = obo+owl / 
    #Give format restrictions 
    file.write('edit_format: owl\n') #To have editable file on ofn format
    file.write('release_artefacts:\n')

    file.write('\t- full\n')
    #Indicate this didn't work like expected (ODK documentation)
    #file.write('\t- base\n')# base, full and simple are three versions of the same ontologie, juste with axioms filters (not imported axioms, not infered axioms ==> see the ODK doc)
    #file.write('\t- simple\n')

    file.write('export_formats:\n')
    file.write('\t- owl\n')

    file.write('github_org: %s\n'%(githubUser))

    #Define quality controls
    file.write('ci:\n')
    file.write('\t- github_actions\n')
    file.close()

    #return create
    YAMLpath="%s/%s"%(ODKPath, projectID)


    return YAMLpath

#------------------------------------------------------------------------------------------ 
#            FUNCTION TO CREATE ODK REPERTORY
#------------------------------------------------------------------------------------------


#/// Edit the YAML config file created automatically by ODK to permit to update the ODK repertory with new tests ///


def editCreatedYAML(projectID): #Permit to edit varable in yaml that odk create in projectID/src/ontology/projectID-odk.yaml (I test to define there variables but that didn't work). If after this function there variables are the same during time and changes

    yamlPath='%s/target/%s/src/ontology'%(ODKPath,projectID)


    substitution1='\'{gsub("release_materialize_object_properties: null","release_materialize_object_properties: []"); print}\''  
    os.system('gawk -i inplace %s %s/%s-odk.yaml'%(substitution1,yamlPath,projectID))

    #The next command didn't work but it's better way codind test replacement in file

   
    #ROBOT test not used with ODK workflow now, but if you want use them in that way indicate them here
    robotTestAdded='  - deprecated_boolean_datatype\n  - deprecated_class_reference\n  - deprecated_property_reference\n  - duplicate_label\n  - missing_label\n  - missing_ontology_description\n  - missing_ontology_license\n  - missing_ontology_title\n  - misused_obsolete_label\n  - misused_replaced_by\n  - multiple_labels\n'


    #To make the file founctional
    os.system('sed -i \'s/uribase_suffix: null/uribase_suffix: \"\"/g\' %s/%s-odk.yaml'%(yamlPath, projectID))




    #So for substitution3 I pass file reading and writing #TODO TODO TODO delete in final code if not used
    file1=open('%s/%s-odk.yaml'%(yamlPath, projectID),'r')
    file2=open('%s/%s-odkREWRITE.yaml'%(yamlPath, projectID),'w')

    parameters=file1.readlines()
    for line in parameters:
        file2.write(line)

    file1.close()
    file2.close()

    os.system('rm %s/%s-odk.yaml'%(yamlPath, projectID))
    os.system('mv %s/%s-odkREWRITE.yaml %s/%s-odk.yaml'%(yamlPath, projectID, yamlPath, projectID))





#/// Update the ODK created repertory with ROBOT tests ///


def firstUpdateODKRepo(projectID,githubUser,gitHub_PassWord,description,interfacePath):  # using update-repo to permit to put the robot tests on the odk command
    
    #Edit the ProjectID-odk.yaml file to avoid error with "make update_repo" command
    editCreatedYAML(projectID)

    projectSrcDir='%s/target/%s/src'%(ODKPath,projectID) #The src directory on ODK project
    print(projectSrcDir)
    
    #Copy the ROBOT SPARQL script into ODK tests repertory
    os.system('cp %s/QualityTests/* %s/sparql/'%(interfacePath,projectSrcDir))

    os.chdir('%s/ontology'%(projectSrcDir))

    subprocess.run(["sh","./run.sh", "make", "update_repo"], capture_output=True, text=True) 
    
    #os.system('sh ./run.sh make update_repo')  #Not work on Christelle PC (LINUX) but on my yes (LINUX too): Replace with subsystem that working






#/// Function that create the ODK repertory, calling the two previous to adding robot tests and create the GitHub repertory to linking it with ODK datas ///


def createODKRepo(projectID,githubUser,gitHub_PassWord,description,interfacePath,inputFileName,inputFileConvertedOwlPath):

    global userMachine,OntoDescr


    parameters='{"name":"%s","description":"%s","private":"true","has_projects":"false","has_wiki":"false"}'%(projectID,description) #json format need ", but we dont want on os.system command symbols ' are intepreted, just printed  
 

    gitRepoCreate=subprocess.run(('curl', '-L', '-X', 'POST', '-H', "Accept: application/vnd.github+json", '-H', "Authorization: Bearer %s"%(gitHub_PassWord), '-H', "X-GitHub-Api-Version: 2022-11-28", 'https://api.github.com/user/repos', '-d', '%s'%(parameters)),capture_output=True,text=True)
    #print('/////////////////',gitRepoCreate)


    os.chdir('%s'%(ODKPath)) #TODO delete on final code
    #print('//////////\n%sseed-via-docker.sh'%(ODKPath))
    os.system('./seed-via-docker.sh -c %s'%(projectID))




    #--- I update ODK repertory with input ontology file
    os.system('robot convert -i %s/TempFiles/%s.owl -o %s/TempFiles/%s.ofn'%(interfacePath, inputFileName, interfacePath, inputFileName))
    os.chdir('%s/target/%s/src/ontology'%(ODKPath, projectID))

    # I have just some line in project-edit.owl file to supress. I chose to write a new empty project-edit.owl without these line to supress the root node

    print("///////////////////////////::::   Edit the ODK editable file")

    file1=open('%s-edit.owl'%(projectID),'r')
    file2=open('%s-editCLEANING.owl'%(projectID),'w')

    lines=file1.readlines()
    for line in lines :
        if "root node" not in line:
            if 'Declaration(Class' not in line and '0000000' not in line:
                file2.write(line)

    file1.close()
    file2.close()

    os.system('rm %s/target/%s/src/ontology/%s-edit.owl'%(ODKPath, projectID, projectID))
    os.system('mv %s/target/%s/src/ontology/%s-editCLEANING.owl %s/target/%s/src/ontology/%s-edit.owl'%(ODKPath,projectID,projectID,ODKPath,projectID,projectID))

    #DEBUG
    #os.system('cp %s/target/%s/src/ontology/%s-edit.owl ~/Document'%(ODKPath,projectID,projectID))
    #

    os.system('robot merge -i %s-edit.owl -i %s/TempFiles/%s.ofn -o MERGED.ofn'%(projectID,interfacePath,inputFileName))

    os.system('rm %s/target/%s/src/ontology/%s-edit.owl'%(ODKPath, projectID, projectID))
    os.system('mv MERGED.ofn %s-edit.owl'%(projectID))


    substitution1='\'{gsub("http://purl.obolibrary.org/obo/TEMP","http://purl.obolibrary.org/obo/%s"); print}\''%(projectID) 
    os.system('gawk -i inplace %s %s-edit.owl'%(substitution1,projectID))

    #--- Update the ODK repo to adding robot quality tests (command report)
    #Do that here permit me to run the ODK command "sh run.sh make update_repo" in ODKrepertory/target/ProjectID/src/ontology
    #That created on this location a new directory, target, like a deeper level in files and I must connect this directory to gitHub
    




    #Now ODK update repo has running and DON'T BE RUNNING AGAIN, i can change the editable file name to according it with this real format
    #os.system('mv %s/target/%s/src/ontology/%s-edit.owl %s/target/%s/src/ontology/%s-edit.ofn'%(ODKPath, projectID, projectID,ODKPath, projectID, projectID))
    

    #Connect github repertory to created odk repertory
    os.chdir('%s/target/%s'%(ODKPath, projectID)) 
    #os.chdir('%s'%(ontoRepWithQCtests)) #To connect new target repetory created after ODK repo update
   
   

    #Create git hub repertory linked to git initialized directory
    os.system('git remote add origin https://%s:%s@github.com/%s/%s.git'%(githubUser,gitHub_PassWord,githubUser,projectID))
   
    os.system('git remote set-url origin https://%s:%s@github.com/%s/%s.git'%(githubUser,gitHub_PassWord,githubUser,projectID))

    #Define the files formats that git large file must manage
    lfsFormatsOFN=subprocess.run(['git','lfs','track',"*.ofn"], capture_output=True, text=True)
    lfsFormatsOWL=subprocess.run(['git','lfs','track',"*.owl"], capture_output=True, text=True)
    lfsFormatsOBO=subprocess.run(['git','lfs','track',"*.obo"], capture_output=True, text=True)
    if lfsFormatsOFN.returncode!=0 or lfsFormatsOWL.returncode!=0 or lfsFormatsOBO.returncode!=0:
        messagebox.showinfo(title=None,message='git extension large files fail')



    os.system('git push -u origin main')

    print("\n\nCreated GitHUB repertory is connect to local files now !")






 
    projectSrcDir='%s/target/%s/src'%(ODKPath,projectID) #The src directory on ODK project
    os.system('cp %s/QualityTests/* %s/sparql/'%(interfacePath,projectSrcDir))


    OntoEditFile='%s/ontology/%s-edit.owl'%(projectSrcDir,projectID)
    searchEmptyTitle=subprocess.run(('grep','-c', 'Annotation(dcterms:title ""',OntoEditFile),capture_output=True,text=True) 
    if searchEmptyTitle.returncode==0:
        putOntoTitle=subprocess.run(('sed','-i', 's/Annotation(dcterms:title ""/Annotation(dcterms:title "%s"/g'%(projectID),OntoEditFile)) 
    searchEmptyDescr=subprocess.run(('grep','-c', 'Annotation(dcterms:description "None"',OntoEditFile),capture_output=True,text=True) 
    if searchEmptyDescr.returncode==0:
        putOntoDescr=subprocess.run(('sed','-i', 's/Annotation(dcterms:description "None"/Annotation(dcterms:description "%s"/g'%(OntoDescr),OntoEditFile)) 


    os.system('git add --all')
    #developper note : I mannually adding title and description because ODK didn't work. Suppress this if finally on the Automatic update that didn't change the editable file
    os.system('git commit -m \'Automatic update\' -m \'Add ROBOT quality tests scripts makes by OntoNet\' -m \'Add ontology title and description\'')
    # -m \'Rename the ontology file according to is real format (OFN)\'') # NOT DOING ANYMORE
    os.system('git push')






#------------------------------------------------------------------------------------------ 
#            A NOTE ABOUT ODK CAPACITY FOR DEVELOPPER - 07 / 06 / 2024
#------------------------------------------------------------------------------------------

#  Normally ODK permit to make git release ponctually, added to user commits. For that, two steps :

# - in ODK/target/project/src/ontology : sh run.sh make prepare_release. That running sparql tests, and if there are OK the main files (like ODK/target/project/project-full.owl) are updated.
#Actual issues : I cant't say to ODK some sparql fails are OK + not sure to change that ont mafile it's a good idea

# - in ODK/target/project/src/ontology : sh run.sh make public_release. That make git realease with command 'gh release
#Actual issues : previous next fail so released file didn't up to date +  token necessary to release didn't take the github token...
#Solution : if release are necessary, put in this tool the gh command and make main file update
