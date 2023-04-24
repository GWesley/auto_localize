# Purpose
Auto translate `Localizable.strings` for multiple languages in Xcode using `Google Translate`、`DeepL` or `OpenAI`. Supports optionally translating missing translations only, given an existing target translation.

# Usage
1. put your origin `Localizable.strings` file in folder
2. `pip3 install -r requirements.txt`
4. `python3 translate.py`
```
usage: translate.py [-h] [-t T] [-a A] [-f F] [-o O] [-d D] [-e E] [-v V]

optional arguments:
  -h, --help  show this help message and exit
  -t T        To set the translator, use the -t option followed by 'deepl' for DeepL, 'google' for Google Translate,
              or 'openai' for OpenAI. OpenAI allow you translate with context from comment. By default, the translator is set to use Google. If you want to use DeepL, you must also specify the authentication key with -a.
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

**NOTE1** Put OpenAI token into `openai_token.txt` before use.

**NOTE2**: Strings that cannot be translated are not copied over to the output directory. This way you
get a chance to correct / modify the original string and try again. When used with the `-d` option, this means that
it will only try and translate the missing strings (i.e. the strings that failed to translate the first time.)

## how to specify custom path to Localizable.strings
`python3 translate.py -f /some/path/to/Localizable.strings`

## how to use DeepL
Google Translate is used by default. To switch to DeepL you must also specify an authentication token, like so:

`python3 translate.py -t deepl -a AUTH_TOKEN_HERE`

## how to use OpenAI
Open AI `text-davinci-003` traslate accuratelly with context from comments. Put token into `openai_token.txt` before use.

`python3 translate.py -t openai`

## how to set origin languge
you can use `-o` to set your origin language,

for example `python3 translate.py -o fr`,

the default origin is english

## how to add more languages
update `LanguageCodes.txt` to add or remove support languages

## how to translate only missing translations
To translate only the strings that have not been translated already, you need to specify the path to the root directory where existing translations reside (i.e. which contains directories such as `fr.lproj` etc):

`python3 translate.py -d ~/path/to/app/resources`

This will then ignore translating any line that already exists.

## how to enable verbose printing
This will print additional information as it translates.
`python3 translate.py -v`

# extract_missing_strings

We already have tools that extract missing localizable strings from code. However, at times you end up with partially incomplete translations
across the different translations you support. For instance
a string may be translated in French but not in Italian, and you may have forgotten to add the same string to your default language (e.g. en.lproj assuming that's
the default locale).

This script helps with this. It scans all supported languages, including your default locale (english if not specified), for
any string which was not found in another translation. It then extracts only the keys and stores them into `Localizable.strings`, ignoring any
that were found in your default locale's `Localizable.strings` file.

This way your default locale's `Localizable.strings` file remains the source of truth. You can then
use `translate.py` to translate any string from this file that does not exist in one of the supported languages,
using the `-d` option to translate only the missing strings.

Usage:

`python3 extract_missing_strings.py -p ~/path/to/app/resources`

The output will be stored under `output/en.lproj/Localizable.strings`
