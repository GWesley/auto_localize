#!/usr/bin/python3
import argparse
import os.path

from functions import readTranslations, clearContentsOfFile, writeTranslationToFile

# At times you end up with partially complete translations across the different translations you support. For instance
# a string may be translated in French but not in Italian, and the same string may not even exist in en.lproj (assuming that's
# the default locale).
#
# This script helps with this. It scans all supported languages, including your default locale (english if not specified), for
# any string which was not found in other translations. It then extracts only the keys and stores them into Localizable.strings
# These can then be translated for all languages using translate.py with the -d option, which would ignore all existing translations.

parser = argparse.ArgumentParser()
parser.add_argument("-p", default="", help="set the path to the root directory where all the localized translations reside (i.e. directory with `fr.lproj` etc)")
parser.add_argument("-o", default="en", help="set the origin locale for to extract missing translations from, default is english")
args = parser.parse_args()

# Read and cache origin language once
resourcePath = os.path.expanduser(args.p.strip())
originLangKey = args.o.strip()
originPath = os.path.join(resourcePath, originLangKey + ".lproj/Localizable.strings")

if not os.path.exists(originPath):
    print("Path not found: %s" % (originPath))
    exit(1)
# endif

originLines = readTranslations(originPath)

# Read languages we must translate to
supportedLanguageCodes = []
supportedLanguageCodes.append(originLangKey)

with open('LanguageCodes.txt', 'r') as supportedLangCodeFile:
    for targetLine in supportedLangCodeFile:
        if targetLine.strip().startswith("#"):
            continue
        #end if

        targetArray = targetLine.split()
        translateFriendlyName = targetArray[0]
        googleTranslateTargetCode = targetArray[1]
        deeplTranslateTargetCode = targetArray[2]
        outputTargetCode = targetArray[3]

        supportedLanguageCodes.append(outputTargetCode)
    #end for
#end with

# Find paths to existing translations for these languages
supportedLanguagePaths = []
for dirpath, dirnames, filenames in os.walk(resourcePath):
    for dirname in dirnames:
        if dirname.find(".lproj") != -1:
            dirLang = dirname.split(os.path.sep)[-1].replace(".lproj", "")

            if dirLang in supportedLanguageCodes:
                localizablePath = os.path.join(os.path.join(dirpath, dirname), "Localizable.strings")
                if not os.path.exists(localizablePath):
                    continue
                #end if
                supportedLanguagePaths.append(localizablePath)
            #endif
        #end if
    #end for
#end for

# Go over each translation, including the default, and find strings that aren't found in other localization files
missingLines = []
missingKeys = []
for supportedLangPath in supportedLanguagePaths:
    print("Reading Localizable.strings from path: %s" % (supportedLangPath))

    supportedLangLines = readTranslations(supportedLangPath)

    # Go over each key
    for langString in supportedLangLines:
        stringName = langString['key']

        # Check if this was seen in every translation
        for otherLangPath in supportedLanguagePaths:
            if otherLangPath == supportedLangPath:
                continue
            #end if

            otherLangLines = readTranslations(otherLangPath)

            didFind = False
            for otherLangString in otherLangLines:
                otherStringName = otherLangString['key']

                if stringName == otherStringName:
                    didFind = True
                    break
                #end if
            # end for

            if not didFind and stringName not in missingKeys:
                missingKeys.append(stringName)
                missingLines.append(langString)
                break
            # end if
        # end for
    #end for
#end for

print("Total missing strings found: %s" % (len(missingLines)))

pathToSave = "Localizable.strings"
clearContentsOfFile(originLangKey)

print("Saving missing localizations")
for missingTrans in missingLines:
    stringName = missingTrans['key']
    stringVal = missingTrans['value']

    # ignore if the key already exists in the original locale
    inOrigin = False
    for originLine in originLines:
        originKey = originLine['key']
        if originKey == stringName:
            inOrigin = True
            break
        #end if
    #end for

    if inOrigin:
        continue
    #end if

    writeTranslationToFile(stringName, stringName, originLangKey)
#end for