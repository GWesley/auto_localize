#!/usr/bin/python3
import argparse
import os.path

from functions import readTranslations, clearContentsOfFile, writeTranslationToFile, writeCommentToFile

#TODO: Auto remove duplicate key / value pairs and report duplicates where their values don't match

# Sorts keys that don't match with their translations to the top of the file. Most of the times the base strings
# file will have lines such as:
# "done" = "done";
#
# However at times you may have something like:
#
# "Preference.General.Done" = "OK";
#
# This script finds such strings and moves them to the top of the file so these can be grouped separately for better
# discoverability.

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

print("Reading source language: %s" % (originPath))

originLines = readTranslations(originPath)

clearContentsOfFile(stringsFileName, originLangKey)

print("Sorting localizations")
totalLinesWritten = 0
mismatchedTranslationLines = []
normalLines = []
for originLine in originLines:
    stringName = originLine['key']
    stringVal = originLine['value']

    if stringName != stringVal:
        mismatchedTranslationLines.append(originLine)

        totalLinesWritten += 1
    #end if
#end for

for originLine in originLines:
    stringName = originLine['key']
    stringVal = originLine['value']

    if stringName == stringVal:
        normalLines.append(originLine)

        totalLinesWritten += 1
    # end if
# end for

formatMisMatch = 0
for line in sorted(mismatchedTranslationLines, key = lambda i: str(i['key']).lower()):
    stringName = line['key']
    stringVal = line['value']
    stringComment = line['comment']

    if not stringComment:
        stringComment = ""
    #end if

    # lint
    stringVal = stringVal.replace("（", " (")
    stringVal = stringVal.replace("）", ") ")
    stringVal = stringVal.replace("％", "%")
    stringVal = stringVal.replace("% @", "%@")
    stringVal = stringVal.replace("\\ n", "\n")

    writeTranslationToFile(stringsFileName, stringName, stringVal, stringComment, originLangKey)

    # Some basic validation to confirm translation did not get rid of formatters in source text
    totalFormattersInSource = stringName.count('%')
    totalFormattersInOutput = stringVal.count('%')

    if totalFormattersInSource != totalFormattersInOutput:
        formatMisMatch += 1

        print("\n  ..... !! WARNING !! Formatters don't match in: %s => %s\n" % (
        stringName, stringVal))
    #end if

    formatterIndex = stringVal.find('%')
    if formatterIndex != -1 and formatterIndex + 1 >= len(stringVal):
        formatMisMatch += 1

        print("\n  ..... !! WARNING !! Invalid formatter in: %s => %s\n" % (stringName, stringVal))
    elif formatterIndex != -1 and len(stringVal) != formatterIndex and stringVal[formatterIndex + 1] not in ['u', 'l', '@', 'f', '1', '2', '3', 'd', '.']:
        formatMisMatch += 1

        print("\n  ..... !! WARNING !! Invalid formatter in: %s => %s\n" % (stringName, stringVal))
    # end if

#end for

writeCommentToFile(stringsFileName, "-------", originLangKey)

for line in sorted(normalLines, key = lambda i: str(i['key']).lower()):
    stringName = line['key']
    stringVal = line['value']
    stringComment = line['comment']

    if not stringComment:
        stringComment = ""
    #end if

    # lint
    stringVal = stringVal.replace("（", " (")
    stringVal = stringVal.replace("）", ")")
    stringVal = stringVal.replace("％", "%")
    stringVal = stringVal.replace("% @", "%@")
    stringVal = stringVal.replace("\\ n", "\n")

    writeTranslationToFile(stringsFileName, stringName, stringVal, stringComment, originLangKey)

    # Some basic validation to confirm translation did not get rid of formatters in source text
    totalFormattersInSource = stringName.count('%')
    totalFormattersInOutput = stringVal.count('%')

    if totalFormattersInSource != totalFormattersInOutput:
        formatMisMatch += 1

        print("\n  ..... !! WARNING !! Formatters don't match in: %s => %s\n" % (
        stringName, stringVal))
    #end if


    formatterIndex = stringVal.find('%')
    if formatterIndex != -1 and formatterIndex + 1 >= len(stringVal):
        formatMisMatch += 1

        print("\n  ..... !! WARNING !! Invalid formatter in: %s => %s\n" % (stringName, stringVal))
    elif formatterIndex != -1 and len(stringVal) != formatterIndex and stringVal[formatterIndex + 1] not in ['u', 'l', '@', 'f', '1', '2', '3', 'd', '.']:
        formatMisMatch += 1

        print("\n  ..... !! WARNING !! Invalid formatter in: %s => %s\n" % (stringName, stringVal))
    # end if
#end for

if formatMisMatch > 0:
    # This may be okay since the string name itself may not have any formatters, but worth pointing out
    # in case the keys and values are the same
    print("WARN: Total mismatched formatters found: %s" % (formatMisMatch))
#endif
if totalLinesWritten != len(originLines):
    print("ERROR: Total lines written do NOT match total lines read - %s != %s" % (totalLinesWritten, len(originLines)))
#end if

print("Done")