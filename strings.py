import re
import requests
import os
import argparse
from googletrans import Translator

translator = Translator()

parser = argparse.ArgumentParser()
parser.add_argument("-o", default="en", help="set the origin locale for auto translation, default is english")
args = parser.parse_args()

def createDirectoryIfNotExists(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))

def writeToFile(sourceText, translatedText, target):
    fileName = "output/" + target + ".lproj/Localizable.strings"
    with open(fileName, "a") as myfile:
        createDirectoryIfNotExists(fileName)
        contentToWrite = "\"" + sourceText + "\" = \"" + translatedText + "\";\n"
        myfile.write(contentToWrite)

def translateSourceText(sourceText, target):
    try:
        obj = translator.translate(sourceText, src=args.o, dest=target)
    except:
        return sourceText   
    return obj.text

def translateLineInFile(line, target, outputTarget):
    matchSource = re.search(r'\"(.*)\"(.*)\"(.*)\"', line)
    if matchSource:
        stringName = matchSource.group(1)
        sourceText = matchSource.group(3)
        translation = translateSourceText(sourceText, target)
        writeToFile(stringName, translation, outputTarget)

def clearContentsOfFile(target):
    fileName = "output/" + target + ".lproj/Localizable.strings"
    createDirectoryIfNotExists(fileName)
    open(fileName, 'w').close()

def translateFile(translateName, target, outputTarget):

    print("Translating for: " + translateName)

    clearContentsOfFile(outputTarget)

    with open('Localizable.strings', 'r') as stringsFile:
        for line in stringsFile:
            translateLineInFile(line, translateTarget, outputTarget)


with open('LanguageCodes.txt', 'r') as targetsFile:
    for targetLine in targetsFile:

        if "#" in targetLine:
            continue
        targetArray = targetLine.split()
        translateName = targetArray[0]
        translateTarget = targetArray[1]
        outputTarget = targetArray[2]

        translateFile(translateName, translateTarget, outputTarget)


