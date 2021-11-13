#!/usr/bin/python3
import argparse
import os.path

from functions import readTranslations, clearContentsOfFile, writeTranslationToFile

# Copies existing translations from another project / app / location.
#
# Use this script when you have another project you wish to copy existing translations from. This will scan all languages
# specified in LanguageCodes.txt in the other location specified and copy any translation it finds for a given key in the specified
# base language (en by default).

parser = argparse.ArgumentParser()
parser.add_argument("-c", default="", help="set the path to the root directory where all the localized translations you wish to copy from reside (i.e. directory with `fr.lproj` etc)")
parser.add_argument("-p", default="", help="set the path to the root directory where the target localized translations you wish to copy to reside (i.e. directory with `fr.lproj` etc)")
parser.add_argument("-f", default="Localizable.strings", help="set the name of the .strings file to look for")
parser.add_argument("-o", default="en", help="set the origin locale, default is english")
args = parser.parse_args()

# Read and cache origin language once
sourceResourcePath = os.path.expanduser(args.c.strip())
targetResourcePath = os.path.expanduser(args.p.strip())
stringsFileName = os.path.expanduser(args.f.strip())
originLangKey = args.o.strip()
targetPath = os.path.join(targetResourcePath, originLangKey + os.path.join(".lproj", stringsFileName))

if not os.path.exists(targetPath):
    print("Path not found: %s" % (targetPath))
    exit(1)
# endif

targetLines = readTranslations(targetPath)

# Read languages we must find translations for
supportedLanguageCodes = []

with open('LanguageCodes.txt', 'r') as supportedLangCodeFile:
    for line in supportedLangCodeFile:
        if line.strip().startswith("#"):
            continue
        #end if

        langArray = line.split()
        translateFriendlyName = langArray[0]
        googleTranslateTargetCode = langArray[1]
        deeplTranslateTargetCode = langArray[2]
        outputTargetCode = langArray[3]

        supportedLanguageCodes.append(outputTargetCode)
    #end for
#end with

# Find paths to source translations
sourceTranslationPaths = []
for dirpath, dirnames, filenames in os.walk(sourceResourcePath):
    for dirname in dirnames:
        if dirname.find(".lproj") != -1:
            dirLang = dirname.split(os.path.sep)[-1].replace(".lproj", "")

            if dirLang in supportedLanguageCodes:
                localizablePath = os.path.join(os.path.join(dirpath, dirname), stringsFileName)
                if not os.path.exists(localizablePath):
                    continue
                #end if
                sourceTranslationPaths.append(localizablePath)
            #endif
        #end if
    #end for
#end for

# Find translations that exist for a given key
for sourceTransPath in sourceTranslationPaths:
    sourceLangName = sourceTransPath.split(os.path.sep)[-2].replace(".lproj", "")

    clearContentsOfFile(stringsFileName, sourceLangName)

    print("Reading %s from source translation '%s' path: %s" % (stringsFileName, sourceLangName, sourceTransPath))

    sourceTransLines = readTranslations(sourceTransPath)

    # Go over each key
    didCopy = 0
    for sourceTransString in sourceTransLines:
        sourceKey = sourceTransString['key']
        sourceTranslation = sourceTransString['value']
        sourceComment = sourceTransString['comment']

        # Copy translation if this key exists in our target default localization file
        for targetLine in targetLines:
            targetKey = targetLine['key']
            if targetKey == sourceKey:
                writeTranslationToFile(stringsFileName, sourceKey, sourceTranslation, sourceComment, sourceLangName)

                didCopy += 1
                break
            # end if
        # end for
    #end for

    print("... Total existing translations copied for '%s': %s" % (sourceLangName, didCopy))
#end for