from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore

import sys, getopt, os, re, time
from pprint import pprint

import lib.ENML_PY as enml
import lib.html2text as html2text

from shotgun_api3 import Shotgun

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def processResources(notebookName, noteTitle, resources, sgNoteId, sg):
    
    for rec in resources:
        
        #Get the file extension
        extension = rec.mime.split('/')[1]

        #If the file doesn't have a name, name it after its Guid
        if not rec.attributes.fileName:
            nome = rec.guid + "." + extension
        else:
            nome = rec.attributes.fileName

        #Create file path
        # recFilePath = '/'.join(['notes', notebookName, noteTitle.replace(' ','_'), nome.replace(' ','_')])
        recFilePath = '/'.join([nome.replace(' ','_')])
        
        # Save the file locally
        print('...Uploading {0}'.format(recFilePath))
        with open(recFilePath, 'w') as recFile:
            recFile.write(rec.data.body)

        # Upload the file as an attachment to the Shotgun note
        sg.upload('Note', sgNoteId, recFilePath)

        # delete the local file
        try:
            os.remove(recFilePath)
        except OSError:
            pass
        
def processTags(noteStore, sgProject, tagGuids, sg):

    noteLinks = []
    
    for tag in tagGuids:
        
        tag = noteStore.getTag(tag)
        tagName = tag.name
        
        #Try to match each tag to an entity in Shotgun
        try:
            entityType, entityName = tagName.split(':')
            entityType = entityType.title()
            noteLink = sg.find(entityType, [['cached_display_name','is',entityName], ['project','is',sgProject[0]]])
            if len(noteLink) == 0:
                print('No matches for {0}, skipping'.format(tagName))
                continue
        except:
            print('No matches for {0}, skipping'.format(tagName))
            continue
        
        noteLinks.append(noteLink[0])
     
    return noteLinks
        
def processNotes(noteStore, notebookName, notes, sg, sgUser):
    
    for noteMetadata in notes:
        
        #Get the note
        note = noteStore.getNote(noteMetadata.guid, False, True, False, False)
        
        #Check if the note was already synced, meaning it has the 'sgSynced' tag
        if note.tagGuids:
            tags = [noteStore.getTag(tagGuid) for tagGuid in note.tagGuids]
            tagNames = [tag.name for tag in tags]
            if 'sgSynced' in tagNames:
                print('\nAlready synced {0}'.format(note.title))
                continue
        
        #Convert the Note body to plain text
        print('\nGetting note data for {0}'.format(noteMetadata.guid))
        contentENML = noteStore.getNoteContent(noteMetadata.guid, True, False, False, False)
        contentHTML = enml.ENMLToHTML(contentENML)
        contentTEXT = html2text.html2text(contentENML.decode('utf-8'))
        contentTEXT = re.sub(r' *\n', os.linesep, contentTEXT)
        
        #Gather the required data for the Shotgun note
        sgProject = sg.find('Project', [['name','is',notebookName]])
        noteLinks = []
        if note.tagGuids:
            print '...Processing tags'
            noteLinks = processTags(noteStore, sgProject, note.tagGuids, sg)
            
        #Create a Shotgun note
        print '...Creating Shotgun note'
        sgData = {'subject':note.title, 'content':contentTEXT, 'project':sgProject[0], 'note_links':noteLinks, 'user':sgUser}
        sgNote = sg.create('Note',sgData)
        
        #If the note has attachments, run processResources() to attachment them to the note
        if note.resources:
            print '...Processing attachments'
            processResources(notebookName, note.title, note.resources, sgNote['id'], sg)
            
        #Tag the note with 'sgSynced' so it doesn't get synced again
        note.tagNames = ['sgSynced']
        noteStore.updateNote(note)

def processNotebook(noteStore, notebook, sg, sgUser):
    
    #Create a simple filter to find all notes in the notebook
    noteFilter = NoteStore.NoteFilter()
    spec = NoteStore.NotesMetadataResultSpec()
    noteFilter.notebookGuid = notebook.guid
    
    #Create a directory to store note attachments
    # createDir('/'.join(['notes', notebook.name.replace(' ','_')]))

    print('\nGetting notes from {0}'.format(notebook.name))
    notesMetadata = noteStore.findNotesMetadata(noteFilter, 0, 1000, spec)

    print('\nProcessing notes - BEGIN')
    processNotes(noteStore, notebook.name, notesMetadata.notes, sg, sgUser)
    print('\nProcessing notes - DONE')

def main(notebookName):
    
    #Get your developer token here: https://www.evernote.com/api/DeveloperToken.action and put it here
    dev_token = ''
    
    #Put your Shotgun script details here
    sg = Shotgun('https://yourSiteName.shotgunstudio.com','shotgun-evernote','yourScriptKey')
    
    #Put your Shotgun user id details here
    sgUserId = 42
    
    sgUser = sg.find_one("HumanUser",[['id', 'is', sgUserId]])

    #Establish a connection to Evernote and store note and user data
    client = EvernoteClient(token=dev_token, sandbox=False)
    userStore = client.get_user_store()
    user = userStore.getUser()

    noteStore = client.get_note_store()

    #Check if the supplied notebook exists, and if it does, send to processNotebook()
    print('\nFinding notebook')
    notebooks = noteStore.listNotebooks()
    notebookNames = [notebook.name for notebook in notebooks]
    if notebookName not in notebookNames:
            print('\nSorry, there are no notebooks in your account named {0}'.format(notebookName))
    else:
        for notebook in notebooks:
            if notebook.name == notebookName:
                print('\nProcessing notebook - BEGIN')
                processNotebook(noteStore, notebook, sg, sgUser)
                print('\nProcessing notebook - DONE\n')
            else:
                continue

if __name__ == '__main__':
    main(sys.argv[1])