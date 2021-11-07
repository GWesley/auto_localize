# auto_localize
Auto translate Localizable.strings for multiple languages in Xcode using Google Translate or DeepL

# Usage
1. put your origin `Localizable.strings` file in folder
2. `pip3 install googletrans==4.0.0-rc1`
3. `pip3 install --upgrade deepl`
4. `python3 translate.py`

![image](https://user-images.githubusercontent.com/2985638/133636085-7e3b7c1b-efcc-430a-a478-383ddd9e634f.png)

# how to specify custom path to Localizable.strings
`python3 translate.py -f /some/path/to/Localizable.strings`

# how to use DeepL
Google Translate is used by default. To switch to DeepL you must also specify an authentication token, like so:

`python3 translate.py -t deepl -a AUTH_TOKEN_HERE`

# how to set origin languge
you can use `-o` to set your origin language,

for example `python3 translate.py -o fr`,

the default origin is english

# how to add more language
update `LanguageCodes.txt` to add or remove support languages

# how to translate only non-translated lines
To translate only the lines that have not been translated already, you need to specify a path to a root directory with existing translations (that contain directories such as `fr.lproj` etc):

`python3 translate.py -d PATH_TO_EXISTING_TRANSLATIONS`

This will then ignore translating any line that already exists. 

# how to enable verbose printing
`python3 translate.py -v`

