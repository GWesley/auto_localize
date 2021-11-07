# auto_localize
Auto translate `Localizable.strings` for multiple languages in Xcode using Google Translate or DeepL. Supports optionally translating missing translations only, given an existing target translation.

# Usage
1. put your origin `Localizable.strings` file in folder
2. `pip3 install googletrans==4.0.0-rc1`
3. `pip3 install --upgrade deepl`
4. `python3 translate.py`
```
usage: translate.py [-h] [-t T] [-a A] [-f F] [-o O] [-d D] [-e E] [-v V]

optional arguments:
  -h, --help  show this help message and exit
  -t T        set the translator to use. -t deepl for DeepL, -t google for Google Translate. Defaults to google. For DeepL
              must also specify auth key with -a
  -a A        set auth key to use for DeepL
  -f F        set the path to the original Localizable.strings to read keys from
  -o O        set the origin locale for auto translation, default is english
  -d D        For delta translations. Set the path to the root directory where existing localized translations exist. If
              specified, this path will be used to check if a line / key has already been translated and skip translating
              that line. This way only the keys that do not exist in the existing destination file will be translated.
  -e E        emulate only. This will not perform any translation but instead emulate and print out details of strings that
              would need to be translated.
  -v V        Verbose
```

**NOTE**: Strings that cannot be translated are not copied over to the output directory. This way you
get a chance to correct / modify the original string and try again. When used with the `-d` option, this means that 
it will only try and translate the missing strings (i.e. the strings that failed to translate the firs time.)

# how to specify custom path to Localizable.strings
`python3 translate.py -f /some/path/to/Localizable.strings`

# how to use DeepL
Google Translate is used by default. To switch to DeepL you must also specify an authentication token, like so:

`python3 translate.py -t deepl -a AUTH_TOKEN_HERE`

# how to set origin languge
you can use `-o` to set your origin language,

for example `python3 translate.py -o fr`,

the default origin is english

# how to add more languages
update `LanguageCodes.txt` to add or remove support languages

# how to translate only missing translations
To translate only the strings that have not been translated already, you need to specify the path to the root directory where existing translations reside (i.e. which contains directories such as `fr.lproj` etc):

`python3 translate.py -d ~/path/to/app/resources`

This will then ignore translating any line that already exists. 

# how to enable verbose printing
This will print additional information as it translates.
`python3 translate.py -v`

