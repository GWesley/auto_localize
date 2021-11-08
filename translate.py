#!/usr/bin/python3
import argparse
import os
import os.path

import deepl
from googletrans import Translator

from functions import readTranslations, writeTranslationToFile, clearContentsOfFile

parser = argparse.ArgumentParser()
parser.add_argument("-t", default="google", help="set the translator to use. -t deepl for DeepL, -t google for Google Translate. Defaults to google. For DeepL must also specify auth key with -a ")
parser.add_argument("-a", default="", help="set auth key to use for DeepL")
parser.add_argument("-f", default="Localizable.strings", help="set the path to the original Localizable.strings to read keys from")
parser.add_argument("-o", default="en", help="set the origin locale for auto translation, default is english")
parser.add_argument("-d", default="", help="For delta translations. Set the path to the root directory where existing localized translations exist. If specified, this path will be used to check if a line / key has already been translated and skip translating that line. This way only the keys that do not exist in the existing destination file will be translated.")
parser.add_argument("-e", default="0", help="emulate only. This will not perform any translation but instead emulate and print out details of strings that would need to be translated.")
parser.add_argument("-v", default="0", help="Verbose")
args = parser.parse_args()

def translateSourceText(sourceText, translateTargetCode):
    """
    Return translation for source text using Google / DeepL
    :param sourceText: source text to translate
    :param translateTargetCode: target language (google translation code)
    :return:
    """

    translatedText = sourceText

    try:
        if str(args.e).strip().lower() == "1":
            if args.v == "1":
                print("  ..... Translating in Emulation: %s" % (sourceText))
            #end if

            pass
        elif str(args.t).strip().lower() == "deepl":
            deeplTranslator = deepl.Translator(args.a)
            result = deeplTranslator.translate_text(sourceText, source_lang=args.o, target_lang=translateTargetCode)

            translatedText = result.text

            if args.v == "1":
                print("  ..... Translated with DeepL: %s => %s" % (sourceText, translatedText))
            #end if
        else:
            googleTranslator = Translator()
            obj = googleTranslator.translate(sourceText, src=args.o, dest=translateTargetCode)

            translatedText = obj.text

            if args.v == "1":
                print("  ..... Translated with Google: %s => %s" % (sourceText, translatedText))
            #end if
        #end if
    except Exception as e:
        if args.v == '1':
            print("\n  ..... !! FAILED !! to translate for %s: %s = %s\n" % (translateTargetCode, sourceText, e))
        #endif
        return (sourceText, False, False)
    #end try

    # Deepl can produce translations with double quotes, we need to escape those properly
    translatedText = translatedText.replace('\\N', '\\n')
    translatedText = translatedText.replace('\\"', '"')
    translatedText = translatedText.replace("\"", "\\\"")

    # Some basic validation to confirm translation did not get rid of formatters in source text
    totalFormattersInSource = sourceText.count('%')
    totalFormattersInOutput = translatedText.count('%')

    if totalFormattersInSource != totalFormattersInOutput:
        print("\n  ..... !! WARNING !! Formatters don't match in: %s => %s (lang: %s)\n" % (sourceText, translatedText, translateTargetCode))
    #end if

    return (translatedText, True, True)
#end def

def translationNeeded(translationTuple, translateTargetCode, existingTranslations):
    """
    Check if translation is required for a given source key. If not delta-translating, this will always return True
    other wise False if translation key found in original target Localizable.strings file.

    :param translationTuple: key / value
    :param translateTargetCode:  target language
    :param existingTranslations:  existing target translations
    :return: True if needed, False if translation was found in the original target.
    """
    stringName = translationTuple['key']
    sourceText = translationTuple['value']

    for existingTranslation in existingTranslations:
        existingKey = existingTranslation['key']
        if existingKey == stringName:
            return False
        #end if
    #end for

    return True
#end def

def translateLineInFile(translationTuple, translateTargetCode, outputTargetCode):
    """
    Translate a given key / value tuple to a target language.

    :param translationTuple: key / value
    :param translateTargetCode:  target language
    :param outputTargetCode:  output target code
    """
    stringName = translationTuple['key']
    sourceText = translationTuple['value']
    stringComment = translationTuple['comment']

    if not stringComment:
        stringComment = ""
    #end if

    (translation, success, warning) = translateSourceText(sourceText, translateTargetCode)

    if success:
        # Only save translated lines
        if str(args.e).strip().lower() == "1":
            # Emulating only
            pass
        else:
            writeTranslationToFile(stringName, translation, stringComment, outputTargetCode)
        #end if
    #end if

    return (success, warning)
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

    # When delta-translating, pre-load existing translations to compare against
    existingOutputTranslations = []
    if len(args.d.strip()) != 0:
        fullExistingPath = os.path.expanduser(args.d.strip())

        pathToExistingFile = os.path.join(fullExistingPath, outputTargetCode + ".lproj/Localizable.strings")

        print("Reading existing Localizable.strings from path: %s" % (pathToExistingFile))

        existingOutputTranslations = readTranslations(pathToExistingFile)

        print("  ... will only translate new keys. Existing translations found: %s keys" % (len(existingOutputTranslations)))
    #end if

    totalLinesTranslated = 0
    totalLinesNeeded = 0
    totalSkipped = 0
    totalWarnings = 0
    for translationTuple in originLines:
        if translationNeeded(translationTuple, translateTargetCode, existingOutputTranslations):
            totalLinesNeeded += 1

            (success, warning) = translateLineInFile(translationTuple, translateTargetCode, outputTargetCode)
            if success:
                totalLinesTranslated += 1
            #end if
            if warning:
                totalWarnings += 1
            #end if
        else:
            totalSkipped += 1
            if args.v == "1":
                print("  ........... skipping already translated key: %s" % (translationTuple['key']))
            #end if
        #end if
    #end for

    if totalWarnings != 0:
        print("ERROR: CHECK WARNINGS. Total reported %s" % (totalWarnings))
    #end if

    if totalLinesNeeded != totalLinesTranslated:
        print("ERROR: NOT ALL LINES TRANSLATED. Total lines translated for %s: %s. Original source count: %s" % (translateFriendlyName, totalLinesTranslated, totalLinesNeeded))
    else:
        if len(args.d.strip()) != 0:
            print("SUCCESS: New lines translated for %s: %s, skipped: %s" % (translateFriendlyName, totalLinesTranslated, totalSkipped))
        else:
            print("SUCCESS: Total lines translated for %s: %s" % (translateFriendlyName, totalLinesTranslated))
        #endif
    #end if
#end def

if str(args.t).strip().lower() == "deepl":
    print("Using DeepL translator")
#endif

# Read and cache origin language once
originPath = os.path.expanduser(args.f.strip())
print("Reading source language: %s" % (originPath))

originLines = readTranslations(originPath)

print("Total lines in source: %s\n" % (len(originLines)))

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

        if deeplTranslateTargetCode.strip() == "-" and str(args.t).strip().lower() == "deepl":
            print("Ignoring non-supported language for DeepL: %s" % (translateFriendlyName))
            continue
        #endif

        useCode = googleTranslateTargetCode
        if str(args.t).strip().lower() == "deepl":
            useCode = deeplTranslateTargetCode
        #end if

        translateFile(translateFriendlyName, useCode, outputTargetCode)

        print("\n")
    #end for
#end def


