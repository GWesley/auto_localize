#!/usr/bin/python3
import argparse
import os.path

from functions import readTranslations, clearContentsOfFile, writeTranslationToFile

# Finds missing strings, not present in the base / default translation, but exist in other translations. Copies these
# back to the base translation.
#
# At times you end up with partially complete translations across the different translations you support. For instance
# a string may be translated in French but not in Italian, and the same string may not even exist in en.lproj (assuming that's
# the default locale).
#
# This script helps with this. It scans all supported languages, including your default locale (english if not specified), for
# any string which was not found in other translations. It then extracts only the keys and stores them into your base Localizable.strings.
# These can then be translated for all languages using translate.py with the -d option (i.e. to perform an incremental, delta translation).

parser = argparse.ArgumentParser()
parser.add_argument("-p", default="", help="set the path to the root directory where all the localized translations reside (i.e. directory with `fr.lproj` etc)")
parser.add_argument("-f", default="Localizable.strings", help="set the name of the .strings file to look for")
parser.add_argument("-o", default="en", help="set the origin locale for to extract missing translations from, default is english")
args = parser.parse_args()

# Read and cache origin language once
resourcePath = os.path.expanduser(args.p.strip())
originLangKey = args.o.strip()
stringsFileName = os.path.expanduser(args.f.strip())
originPath = os.path.join(resourcePath, originLangKey + os.path.join(".lproj", stringsFileName))

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
                localizablePath = os.path.join(os.path.join(dirpath, dirname), stringsFileName)
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
    print("Reading %s from path: %s" % (stringsFileName, supportedLangPath))

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

clearContentsOfFile(stringsFileName, originLangKey)

print("Saving missing localizations")
totalLinesWritten = 0
for missingTrans in sorted(missingLines, key = lambda i: str(i['key']).lower()):
    stringName = missingTrans['key']
    stringVal = missingTrans['value']
    stringComment = missingTrans['comment']

    if not stringComment:
        stringComment = ""
    #end if

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

    writeTranslationToFile(stringsFileName, stringName, stringName, stringComment, originLangKey)

    totalLinesWritten += 1
#end for

print("Total lines written: %s, already in origin: %s" % (totalLinesWritten, len(missingLines)-totalLinesWritten))