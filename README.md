evernote-shotgun
================

Upload any Evernote Notebook and all its notes and attachments to a Shotgun Project.

## Minimum Requirements

* Shotgun server
* Evernote account
* Python v2.7

## Installation

1. Download the Zip from this repository
2. Update evernote-shotgun.py file with the following values: 
    - Evernote Developer key (line 135)
    - Shotgun URL, Shotgun Script name, Shotgun API key (line 138)
    - Shotgun HumanUser Id (line 141)

3. Run the following commands in the terminal (make sure [pip](https://pip.pypa.io/en/latest/installing.html) is installed):
<pre>
     sudo pip install evernote
     sudo pip install BeautifulSoup4
</code>

## Usage

1. Make sure your Notebook in Evernote matches your Project name exactly in Shotgun.
1. Run the following command to launch script (make sure to run it from a directory where you have read/write priveleges, such as your Desktop or Downloads):
<pre>
     python /path/to/the/script/evernote-shotgun-master/evernote-shotgun.py 'Your Project Name'
</code>

## Tips

* Shotgun Project must already exist and exactly match the name of your Evernote Notebook (case sensitive)
* Evernote Tags are used to link Notes to Shotgun entities following this syntax: entityType:EntityName (e.g. asset:Squirrel or shot:001_010)
* Once you run the script, each uploaded Note will receive an 'sgSynced' Tag in Evernote, which tells the script to ignore the note if you run the script again
