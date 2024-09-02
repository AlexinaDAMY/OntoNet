##################################################
#           ONTONET NOTE
##################################################

# OntoNet is a master student's internship project. It developped in the Transcriptional Control of Chordate Morphogenesis team, on the Center of Research in Cellular Biology of Montpellier (CRBM) in CNRS. OntoNet goal it's to provide an interfaced and automatized way to manage ontology files, with quality controls.

##################################################

import sys
import os
import subprocess
from subprocess import check_output
from subprocess import Popen, PIPE


from tkinter import * 
from tkinter.ttk import * 
from tkinter import messagebox


#--------------------
# Some variable that can change 
#--------------------

#No variable now

#------------------------------------------------------------------------------------------
#            FUNCTION TO CLEANING FILE (if it's OBO) TO DIDN'T SYNTAX ERRORS
#                     IN A SET OF ERRORS FINDED IN DELPHINE'S FILES
#------------------------------------------------------------------------------------------



def OBO_CLEANING(filePath,outputFilePath,RepoForTempFiles):

    #Define each existing tag in OBO format
    existingTags=["is_obsolete","comment", "def", "relationship", "is_a created_by", "creation_date", "name", "namespace", "default-namespace", "ontology", "format-version", "date", "saved-by", "auto-generated-by", "is_anonymous",  "domain", "range", "as_anti_symmetric", "is_cyclic", "is_reflexive", "is_symmetric", "is_transitive", "is_functional", "is_inverse_functional", "instance_of", "intersection_of", "union_of", "is_metedata_tag", "is_class_level"]

    #A file to save errors can occur during OBO correction
    errorFile=open('%s/LastOBOcleaningReport'%(RepoForTempFiles),'w')

    errorFile.write('INPUT FILE : %s\n\n'%(filePath))



    #Define each total FIXED syntax errors number
    cptCorrEndTab=0
    cptCorrTabIn=0
    cptCorrBadTag=0
    cptCorrMissUnderscore=0
    cptCorrSpaceAfterDate=0
    cptCorrMissNewline=0
    cptCorrMissSpace=0
    cptCorrSpecialCar=0

    cptGrepErrors=0 #Number of lines where subprocess grep motif fail !


    errorFile.write('\n\nOUTPUT FILE : %s\n\n'%(outputFilePath))

    copyInputFile=subprocess.run(['cp',filePath,outputFilePath],capture_output=True,text=True)

    if copyInputFile.returncode!=0:
        print('\n\nERROR : UNABLE TO COPY INPUT FILE')
        messagebox.showerror(title=NONE, message='Input file copy fail : see terminal')
        print(copyInputFile)

    else:

        #Remove any special caractère on cleaning file :

            #--Test OS
        OSTest=subprocess.run(['uname', '-o'],capture_output=True,text=True)
        print('****************** ',OSTest,'\n',OSTest.stdout)
        if 'Darwin' in OSTest.stdout:
            OS='Mac'
        else:
            OS='Not Mac'

        print('---------- ',OS)

            #--Command according to the OS
        if OS=='Mac':
            cleanSpeCar=subprocess.run(['sed','-E','-i','\'\'', 's/[^[:print:]\t]//g', outputFilePath],capture_output=True,text=True)
        else:
            cleanSpeCar=subprocess.run(['sed','-E','-i', 's/[^[:print:]\t]//g', outputFilePath],capture_output=True,text=True)

        if cleanSpeCar.returncode!=0:
            print('\n\nERROR : UNABLE TO REMOVE SPECIAL CARACTER IN INPUT FILE')
            messagebox.showerror(title=NONE, message='Input file special caracter cleaning fail : see terminal')
            print(cleanSpeCar)                       


    #__________________Remove TAB at end of the lines
        print('"\n----------------------------------------------------\nRemove tab at end of line\n----------------------------------------------------\n"')
        errorFile.write('\n\n\n__________________Remove TAB at end of the lines\n')

        cptLineEndTab=subprocess.run(('grep','-E','-c', '\t{1,}$', filePath),capture_output=True,text=True)  
            
        if cptLineEndTab.returncode!=0 and cptLineEndTab.returncode!=1:
            #Inform developper on terminal
            print('ERROR\n')
            print(cptLineEndTab)
            #Inform developper on LastCleaning file on Temps file repertory
            errorFile.write('ERROR\n')
            errorFile.write('returncode : %s\nprinted : %s'%(cptLineEndTab.returncode,cptLineEndTab.stdout))
            #Inform user in interface
            cptCorrEndTab='FAILED !'
        else:
            errorFile.write('Count errors on file working')
            cptCorrEndTab=int(cptLineEndTab.stdout[0:-1])

        if cptLineEndTab.returncode==0:
            errorFile.write('\nAt least one case has been detected.')

            if OS=='Mac':
                replacement=subprocess.run(('sed','-E','-i','\'\'', "s/\t{1,}$//g", outputFilePath),capture_output=True,text=True)
            else:
                replacement=subprocess.run(('sed','-E','-i', "s/\t{1,}$//g", outputFilePath),capture_output=True,text=True)

            if replacement.returncode!=0:
                #Inform developper on terminal
                print('ERROR\n')
                print(replacement)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                #Inform user in interface
                cptCorrEndTab='FAILED !' #If not replaced, the count must be this event if we know number of errors

            else:
                errorFile.write(' Correction : OK')

    #__________________Replace TAB inside line by space

        print('"\n----------------------------------------------------\nReplace TAB inside line by space\n----------------------------------------------------\n"')
        errorFile.write('\n\n\n__________________Replace TAB inside line by space\n')

        cptLineTabIn=subprocess.run(('grep','-E','-c', "\t{1,}", outputFilePath),capture_output=True,text=True)  #Count TAB after endedTAB correction
            
        if cptLineTabIn.returncode!=0 and cptLineTabIn.returncode!=1:
            #Inform developper on terminal
            print('ERROR\n')
            print(cptLineTabIn)
            #Inform developper on LastCleaning file on Temps file repertory
            errorFile.write('ERROR\n')
            errorFile.write('returncode : %s\nprinted : %s'%(cptLineTabIn.returncode,cptLineTabIn.stdout))
            #Inform user in interface
            cptCorrTabIn='FAILED !'
        else:
            errorFile.write('Count errors on file working')
            cptCorrTabIn=int(cptLineTabIn.stdout[0:-1])

        if cptLineTabIn.returncode==0:
            errorFile.write('\nAt least one case has been detected.')
            
            if OS=='Mac':
                replacement=subprocess.run(('sed', "-E",'-i','\'\'', "s/\t{1,}/ /g", outputFilePath),capture_output=True,text=True)
            else:
                replacement=subprocess.run(('sed','-i', "-E", "s/\t{1,}/ /g", outputFilePath),capture_output=True,text=True)

            if replacement.returncode!=0:
                #Inform developper on terminal
                print('ERROR\n')
                print(replacement)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                #Inform user in interface
                cptCorrTabIn='FAILED !' #If not replaced, the count must be this event if we know number of errors

            else:
                errorFile.write(' Correction : OK')


    #__________________Put forget '\n' after '[ANISEED:]' at the end of line
        
        print('\n----------------------------------------------------\nPut forget \'\n\' after \'[ANISEED:]\' at the end of line\n----------------------------------------------------\n')
        errorFile.write('\n\n\n__________________Put forget \'\\n\' after \'[ANISEED:]\' at the end of line\n')


        cptLineMissNewline=subprocess.run(('grep','-cE','ANISEED:][A-Za-z0-9 ]', filePath),capture_output=True,text=True)  
            
        if cptLineMissNewline.returncode!=0 and cptLineMissNewline.returncode!=1:
            #Inform developper on terminal
            print('ERROR\n')
            print(cptLineMissNewline)
            #Inform developper on LastCleaning file on Temps file repertory
            errorFile.write('ERROR\n')
            errorFile.write('returncode : %s\nprinted : %s'%(cptLineMissNewline.returncode,cptLineMissNewline.stdout))
            #Inform user in interface
            cptCorrMissNewline='FAILED !'
        else:
            errorFile.write('Count errors on file working')
            cptCorrMissNewline=int(cptLineMissNewline.stdout[0:-1])

        if cptLineMissNewline.returncode==0: #If error is finded
            errorFile.write('\nAt least one case has been detected.')


        #---- FIRST, just remove if it's space(s) after [ANISEED:]

            if OS=='Mac':
                replacement=subprocess.run(('sed','-E','-i','\'\'', "s/ANISEED:] {1,}\\n/ANISEED:]\\n/g", outputFilePath),capture_output=True,text=True)
            else:
                replacement=subprocess.run(('sed','-E','-i', "s/ANISEED:] {1,}\\n/ANISEED:]\\n/g", outputFilePath),capture_output=True,text=True)

            if replacement.returncode!=0:
                #Inform developper on terminal
                print('ERROR\n')
                print(replacement)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                #Inform user in interface
                cptCorrMissNewline='FAILED !' #If not replaced, the count must be this event if we know number of errors

        #---- AFTER : include missing \n if something after [ANISEED:]

            if OS=='Mac':
                replacement=subprocess.run(('sed','-E','-i','\'\'', "s/ANISEED:]([^\\n])/ANISEED:]\\n\\1/g", outputFilePath),capture_output=True,text=True)
            else:
                replacement=subprocess.run(('sed','-E','-i', "s/ANISEED:]([^\\n])/ANISEED:]\\n\\1/g", outputFilePath),capture_output=True,text=True)

            if replacement.returncode!=0:
                #Inform developper on terminal
                print('ERROR\n')
                print(replacement)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                #Inform user in interface
                cptCorrMissNewline='FAILED !' #If not replaced, the count must be this event if we know number of errors

            else:
                errorFile.write(' Correction : OK')




    #__________________obo TAG correction 


        print('\n----------------------------------------------------\nobo double TAG correction\n----------------------------------------------------\n')
        errorFile.write('\n\n\n__________________obo double TAG correction\n')

        for tag in existingTags :

            cptLineBadTag=subprocess.run(('grep','-c', "^%s: %s:"%(tag,tag), filePath),capture_output=True,text=True)  
            
            if cptLineBadTag.returncode!=0 and cptLineBadTag.returncode!=1:
                #Inform developper on terminal
                print('ERROR\n')
                print(cptLineBadTag)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('ERROR\n')
                errorFile.write('returncode : %s\nprinted : %s'%(cptLineBadTag.returncode,cptLineBadTag.stdout))
                #Inform user in interface
                if cptCorrBadTag[0:5]!='FAILED':
                    cptCorrBadTag='FAILED !'
                cptCorrBadTag+='(%s)'%(tag)
            else:
                errorFile.write('\nTAG : %s - Count errors on file working'%(tag))
                cptCorrBadTag=cptCorrBadTag+int(cptLineBadTag.stdout[0:-1])

            if cptLineBadTag.returncode==0:
                errorFile.write('\nAt least one case has been detected.')

                if OS=='Mac':
                    replacement=subprocess.run(('sed','-i','\'\'', 's/^%s: %s:/%s: /g'%(tag,tag,tag), outputFilePath),capture_output=True,text=True)
                else:
                    replacement=subprocess.run(('sed','-i', 's/^%s: %s:/%s: /g'%(tag,tag,tag), outputFilePath),capture_output=True,text=True)

                if replacement.returncode!=0:
                    #Inform developper on terminal
                    print('ERROR\n')
                    print(replacement)
                    #Inform developper on LastCleaning file on Temps file repertory
                    errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                    errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                    #Inform user in interface
                    if cptCorrBadTag[0:5]!='FAILED':  #If not replaced, the count must be this event if we know number of errors
                        cptCorrBadTag='FAILED !'
                    cptCorrBadTag+='(%s)'%(tag)

                else:
                    errorFile.write(' Correction : OK')




    #__________________Put the forget space after tag:


        print('\n----------------------------------------------------\nPut the forget space after tag:\n----------------------------------------------------\n')
        errorFile.write('\n\n\n__________________Put the forget space after tag:\n')

        for tag in existingTags :

            cptLineMissSpace=subprocess.run(('grep','-c', "^%s:[^ ]"%(tag), filePath),capture_output=True,text=True)  
            
            if cptLineMissSpace.returncode!=0 and cptLineBadTag.returncode!=1:
                #Inform developper on terminal
                print('ERROR\n')
                print(cptLineMissSpace)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('ERROR\n')
                errorFile.write('returncode : %s\nprinted : %s'%(cptLineMissSpace.returncode,cptLineMissSpace.stdout))
                #Inform user in interface
                if cptCorrMissSpace[0:5]!='FAILED':
                    cptCorrMissSpace='FAILED !'
                cptCorrMissSpace+='(%s)'%(tag)
            else:
                errorFile.write('\nTAG : %s - Count errors on file working'%(tag))
                cptCorrMissSpace=cptCorrMissSpace+int(cptLineMissSpace.stdout[0:-1])

            if cptLineMissSpace.returncode==0:
                errorFile.write('\nAt least one case has been detected.')

                if OS=='Mac':
                    replacement=subprocess.run(('sed','-i','\'\'', 's/^\(%s:\)\([^ ]\)/\\1 \\2/g'%(tag), outputFilePath),capture_output=True,text=True)
                else:
                    replacement=subprocess.run(('sed','-i', 's/^\(%s:\)\([^ ]\)/\\1 \\2/g'%(tag), outputFilePath),capture_output=True,text=True)

                if replacement.returncode!=0:
                    #Inform developper on terminal
                    print('ERROR\n')
                    print(replacement)
                    #Inform developper on LastCleaning file on Temps file repertory
                    errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                    errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                    #Inform user in interface
                    if cptCorrMissSpace[0:5]!='FAILED':  #If not replaced, the count must be this event if we know number of errors
                        cptCorrMissSpace='FAILED !'
                    cptCorrMissSpace+='(%s)'%(tag)

                else:
                    errorFile.write(' Correction : OK')


#__________________Give '_' symbole to each namespace  


        print('\n----------------------------------------------------\nGive \'_\' symbole to each namespace\n----------------------------------------------------\n')
        errorFile.write('\n\n\n__________________Give \'_\' symbole to each namespace\n')

        cptLineMissUnderscore=subprocess.run(('grep','-Ec',"^namespace: [A-Za-z0-9]* [A-Za-z0-9]*", filePath),capture_output=True,text=True)  
            
        if cptLineMissUnderscore.returncode!=0 and cptLineMissUnderscore.returncode!=1:
            #Inform developper on terminal
            print('ERROR\n')
            print(cptLineMissUnderscore)
            #Inform developper on LastCleaning file on Temps file repertory
            errorFile.write('ERROR\n')
            errorFile.write('returncode : %s\nprinted : %s'%(cptLineMissUnderscore.returncode,cptLineMissUnderscore.stdout))
            #Inform user in interface
            cptCorrMissUnderscore='FAILED !'
        else:
            errorFile.write('Count errors on file working')
            cptCorrMissUnderscore=int(cptLineMissUnderscore.stdout[0:-1])

        if cptLineMissUnderscore.returncode==0:
            errorFile.write('\nAt least one case has been detected.')

            if OS=='Mac':
                replacement=subprocess.run(('sed','-E', '-i','\'\'', "s/^(namespace: )([A-Za-z0-9]*)( )([A-Za-z0-9]*)/\\1\\2_\\4/g", outputFilePath),capture_output=True,text=True)
            else:
                replacement=subprocess.run(('sed','-i','-E', "s/^(namespace: )([A-Za-z0-9]*)( )([A-Za-z0-9]*)/\\1\\2_\\4/g", outputFilePath),capture_output=True,text=True)

            if replacement.returncode!=0:
                #Inform developper on terminal
                print('ERROR\n')
                print(replacement)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK thast write so reader know it's for sed command
                errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                #Inform user in interface
                cptCorrMissUnderscore='FAILED !' #If not replaced, the count must be this event if we know number of errors

            else:
                errorFile.write(' Correction : OK')




#__________________Unexpected space after date


        print('\n----------------------------------------------------\nUnexpected space after date\n----------------------------------------------------\n')
        errorFile.write('\n\n\n__________________Unexpected space after date\n')

        cptLineSpaceAfterDate=subprocess.run(('grep','-cE',"[0-9]{2}/[0-9]{2}/[0-9]{4} :", filePath),capture_output=True,text=True)  
            
        if cptLineSpaceAfterDate.returncode!=0 and cptLineSpaceAfterDate.returncode!=1:
            #Inform developper on terminal
            print('ERROR\n')
            print(cptLineSpaceAfterDate)
            #Inform developper on LastCleaning file on Temps file repertory
            errorFile.write('ERROR\n')
            errorFile.write('returncode : %s\nprinted : %s'%(cptLineSpaceAfterDate.returncode,cptLineSpaceAfterDate.stdout))
            #Inform user in interface
            cptCorrSpaceAfterDate='FAILED !'
        else:
            errorFile.write('Count errors on file working')
            cptCorrSpaceAfterDate=int(cptLineSpaceAfterDate.stdout[0:-1])

        if cptLineSpaceAfterDate.returncode==0:
            errorFile.write('\nAt least one case has been detected.')
            
            if OS=='Mac':
                replacement=subprocess.run(('sed','-E','-i','\'\'', "s/([0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]) /\\1/g", outputFilePath),capture_output=True,text=True) #if regex (-E) didn't need escape '('
            else:
                replacement=subprocess.run(('sed','-E','-i', "s/([0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]) /\\1/g", outputFilePath),capture_output=True,text=True) #if regex (-E) didn't need escape '('
          
            if replacement.returncode!=0:
                #Inform developper on terminal
                print('ERROR\n')
                print(replacement)
                #Inform developper on LastCleaning file on Temps file repertory
                errorFile.write('Correction : ERROR\n') #Not write if grep error before and if grep OK that write so reader know it's for sed command
                errorFile.write('returncode : %s\nprinted : %s'%(replacement.returncode,replacement.stdout))
                #Inform user in interface
                cptCorrSpaceAfterDate='FAILED !' #If not replaced, the count must be this event if we know number of errors

            else:
                errorFile.write(' Correction : OK')





    errorFile.close()

   
    printeChanges(outputFilePath,cptCorrEndTab,cptCorrTabIn,cptCorrBadTag,cptCorrMissUnderscore,cptCorrSpaceAfterDate,cptCorrMissNewline,cptCorrMissSpace,cptGrepErrors)


    #Variable to know if some errors are corrected in the file
    if cptCorrEndTab==0 and cptCorrTabIn==0 and cptCorrBadTag==0 and cptCorrMissUnderscore==0 and cptCorrSpaceAfterDate==0 and cptCorrMissNewline==0 and cptCorrMissSpace==0 :
        corrStatus='No errors'

    else:
        corrStatus='Errors'

    return corrStatus




#------------------------------------------------------------------------------------------
#                    FUNCTION TO DISPLAY NUMBER OF CORRECTED ERRORS
#------------------------------------------------------------------------------------------


def printeChanges(outputFilePath,cptCorrEndTab,cptCorrTabIn,cptCorrBadTag,cptCorrMissUnderscore,cptCorrSpaceAfterDate,cptCorrMissNewline,cptCorrMissSpace,cptGrepErrors):

    win=Toplevel()
    win.title('Syntaxical error was corrected')
    win.geometry("600x550")

    if cptGrepErrors>0:
        
        messagebox.showerror(title=None, message='Some error correction failed !')
        

    message=Label(win, text='The following errors was detected and corrected in the file \n%s : '%(outputFilePath))
    error1=Label(win,text='TAB(s) at the end of line removed : %s line(s)'%(cptCorrEndTab))
    error2=Label(win,text='TAB(s) on the line replaces by one space : %s line(s)'%(cptCorrTabIn))
    error3=Label(win,text='Tag starting line duplicated rewrite once : %s line(s)'%(cptCorrBadTag))
    error4=Label(win,text='Missing space(s) after tag : %s added'%(cptCorrMissSpace))
    error5=Label(win,text='Space(s) between date(s) and ":" symbol removed: %s lines'%(cptCorrSpaceAfterDate))
    error6=Label(win,text='Space(s) in namespace terms replaced by underscore : %s term(s)'%(cptCorrMissUnderscore))
    error7=Label(win,text='Missing newline symbol(s) between \'[ANISEED:]\' and tag\nOr remove space(s) after \'[ANISEED:]\' : %s added'%(cptCorrMissNewline))

    message.pack(pady=45)
    error1.pack()
    error2.pack(pady=30)
    error3.pack()
    error4.pack(pady=30)
    error5.pack()
    error6.pack(pady=30)
    error7.pack()