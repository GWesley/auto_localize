import re
import os
import argparse
from googletrans import Translator

translator = Translator()

parser = argparse.ArgumentParser()
parser.add_argument("-f", default="Localizable.strings", help="set the path to the original Localizable.strings to read keys from")
parser.add_argument("-o", default="en", help="set the origin locale for auto translation, default is english")
parser.add_argument("-d", default="", help="For delta translations. Set the path to the root directory where existing localized translations exist. If specified, this path will be used to check if a line / key has already been translated and skip translating that line. This way only the keys that do not exist in the existing destination file will be translated.")
parser.add_argument("-v", default="1", help="Verbose")
args = parser.parse_args()

# Read and cache origin language once
print("Reading source language: %s" % (args.f))

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

            translationTuple = (stringName, sourceText)

            originLines.append(translationTuple)
        else:
            if args.v == '1':
                print("   ignoring source line: %s" % (line))
            #end if
        #end if
    # end for
# end with

print("Total lines in source: %s\n" % (len(originLines)))

def createOutputDirectoryIfNotExists(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))
    #end if
#end def

def writeToFile(sourceText, translatedText, outputTargetCode):
    fileName = "output/" + outputTargetCode + ".lproj/Localizable.strings"
    with open(fileName, "a") as myfile:
        createOutputDirectoryIfNotExists(fileName)
        contentToWrite = "\"" + sourceText + "\" = \"" + translatedText + "\";\n"
        myfile.write(contentToWrite)
    #end with
#end def

def translateSourceText(sourceText, translateTargetCode):
    """
    Return translation for source text
    :param sourceText: source text to translate
    :param translateTargetCode: target language (google translation code)
    :return:
    """
    try:
        obj = translator.translate(sourceText, src=args.o, dest=translateTargetCode)
    except Exception as e:
        if args.v == '1':
            print("   FAILED to translate for %s: %s = %s" % (translateTargetCode, sourceText, e))
        #endif
        return (sourceText, False)
    #end try

    return (obj.text, True)
#end def

def translationNeeded(translationTuple, translateTargetCode, outputTargetCode):
    """
    Check if translation is required for a given source key. If not delta-translating, this will always return True
    other wise False if translation key found in original target Localizable.strings file.

    :param translationTuple: key / value
    :param translateTargetCode:  target language
    :param outputTargetCode:  traget output file
    :return: True if needed, False if translation was found in the original target.
    """
    stringName = translationTuple[0]
    sourceText = translationTuple[1]

    return True
#end def

def translateLineInFile(translationTuple, translateTargetCode, outputTargetCode):
    """
    Translate a given key / value tuple to a target language.

    :param translationTuple: key / value
    :param translateTargetCode:  target language
    :param outputTargetCode:  output target code
    """
    stringName = translationTuple[0]
    sourceText = translationTuple[1]

    (translation, success) = translateSourceText(sourceText, translateTargetCode)

    writeToFile(stringName, translation, outputTargetCode)

    return success
#end def

def clearContentsOfFile(target):
    fileName = "output/" + target + ".lproj/Localizable.strings"
    createOutputDirectoryIfNotExists(fileName)
    open(fileName, 'w').close()
#end def

def translateFile(translateFriendlyName, translateTargetCode, outputTargetCode):
    """
    Translate source language for the given target language / output file
    :param translateFriendlyName: friendly name for printing
    :param translateTargetCode: google translation target code
    :param outputTargetCode: output target code
    :return:
    """
    print("Translating for: " + translateFriendlyName)

    clearContentsOfFile(outputTargetCode)

    totalLinesTranslated = 0
    totalLinesNeeded = 0
    for translationTuple in originLines:
        if translationNeeded(translationTuple, translateTargetCode, outputTargetCode):
            totalLinesNeeded += 1

            if translateLineInFile(translationTuple, translateTargetCode, outputTargetCode):
                totalLinesTranslated += 1
            #end if
        #end if
    #end for

    if totalLinesNeeded != totalLinesTranslated:
        print("    WARNING: Total lines translated: %s. Original source count: %s" % (totalLinesTranslated, totalLinesNeeded))
    #end if
#end def

with open('LanguageCodes.txt', 'r') as supportedLangCodeFile:
    for targetLine in supportedLangCodeFile:

        if targetLine.strip().startswith("#"):
            continue
        #end if

        targetArray = targetLine.split()
        translateFriendlyName = targetArray[0]
        translateTargetCode = targetArray[1]
        outputTargetCode = targetArray[2]

        translateFile(translateFriendlyName, translateTargetCode, outputTargetCode)
    #end for
#end def


