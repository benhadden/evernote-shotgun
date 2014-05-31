evernote-shotgun
================

Upload any Evernote Notebook and all its notes and attachments to a Shotgun Project.

## Minimum Requirements

* Shotgun server
* Evernote account
* Python v2.7

## Installation

* Download the master branch
* Input your Evernote Developer key, Shotgun server / script info, and Shotgun User ID to the evernote-shotgun.py file.

## Usage

    python evernote-shotgun '[Shotgun Project Name]'

## Documentation

* Shotgun Project must already exist and exactly match the name of your Evernote Notebook (case sensitive)
* Evernote Tags are used to link Notes to Shotgun entities following this syntax: EntityType:EntityName (e.g. Asset:Squirrel or Shot:001_010)
* Once you run the script, each uploaded Note will receive an 'sgSynced' Tag in Evernote, which tells the script to ignore the note if you run the script again