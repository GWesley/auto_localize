import re
import os
import argparse
from googletrans import Translator

translator = Translator()

parser = argparse.ArgumentParser()
parser.add_argument("-f", default="Localizable.strings", help="set the path to the original Localizable.strings to read keys from")
parser.add_argument("-o", default="en", help="set the origin locale for auto translation, default is english")
parser.add_argument("-v", default="1", help="Verbose")
args = parser.parse_args()

# Read and cache origin language once
originLines = []
with open(args.f, 'r') as stringsFile:
    for line in stringsFile:
        # Ignore empty lines
        if len(line.strip()) == 0:
            continue
        # endif

        # Ignore lines we cannot translate
        matchSource = re.search(r'\"(.*)\"(.*)\"(.*)\"', line)
        if matchSource:
            stringName = matchSource.group(1)
            sourceText = matchSource.group(3)

            translationCouple = (stringName, sourceText)

            originLines.append(translationCouple)
        else:
            if args.v == '1':
                print("   ignoring source line: %s" % (line))
            #end if
        #end if
    # end for
# end with

def createDirectoryIfNotExists(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))
    #end if
#end def

def writeToFile(sourceText, translatedText, target):
    fileName = "output/" + target + ".lproj/Localizable.strings"
    with open(fileName, "a") as myfile:
        createDirectoryIfNotExists(fileName)
        contentToWrite = "\"" + sourceText + "\" = \"" + translatedText + "\";\n"
        myfile.write(contentToWrite)
    #end with
#end def

def translateSourceText(sourceText, target):
    try:
        obj = translator.translate(sourceText, src=args.o, dest=target)
    except Exception as e:
        print("   translation failed for: %s = %s" % (sourceText, e))
        return sourceText   
    return obj.text
#end def

def translateLineInFile(translationCouple, target, outputTarget):
    stringName = translationCouple[0]
    sourceText = translationCouple[1]

    translation = translateSourceText(sourceText, target)
    writeToFile(stringName, translation, outputTarget)
#end def

def clearContentsOfFile(target):
    fileName = "output/" + target + ".lproj/Localizable.strings"
    createDirectoryIfNotExists(fileName)
    open(fileName, 'w').close()
#end def

def translateFile(translateName, target, outputTarget):
    print("Translating for: " + translateName)

    clearContentsOfFile(outputTarget)

    for translationCouple in originLines:
        translateLineInFile(translationCouple, translateTarget, outputTarget)
    #end for
#end def


with open('LanguageCodes.txt', 'r') as targetsFile:
    for targetLine in targetsFile:

        if "#" in targetLine:
            continue
        targetArray = targetLine.split()
        translateName = targetArray[0]
        translateTarget = targetArray[1]
        outputTarget = targetArray[2]

        translateFile(translateName, translateTarget, outputTarget)
    #end for
#end def


