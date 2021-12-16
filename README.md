# ghost-theme-poster
Post ghost themes using script

## Ghost requirements: 
Create a new integration in the admin panel, where you get the admin key. It's the longer one with a ':' in it. 

## Installation
/!\ Create and activate a virtual environment if you please. 

```
git clone https://github.com/educationwarehouse/ghost-theme-poster
cd ghost-theme-poster 
pip install -r requirements.txt
echo example.tld: YOUR:TOKENFROMANEWINTEGRATIONINGHOSTADMIN > .ghost-keys 
```

## Configuration
Go to ghost admin's page, navigate to the themes and download the theme.  
Create a new folder with the name of the domain (example.tld) and unpack the contents of the theme in that folder. 

Repeat this for every domain you'll be creating ghost templates for. 

Change the files as you please, and perform the execution to: 
 1. pack the files into `example.tld.zip` 
 1. upload the theme folder to the ghost domain 
 1. read error or confirmation from the console.

## Execution
```
invoke push example.tld 
```
If the theme is set active in the admin panel, and it passes validation, it will be activated automatically.  
If validation fails, you'll receive the formatted json error message. 

