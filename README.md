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

## Execution
```
invoke push example.tld 
```
If the theme is set active in the admin panel, and it passes validation, it will be activated automatically.  
If validation fails, you'll receive the formatted json error message. 

