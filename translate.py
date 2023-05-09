#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import os.path

import deepl
from googletrans import Translator
import openai

# from googletrans import Translator

from functions import readTranslations, writeTranslationToFile, clearContentsOfFile, read_open_ai_token
parser = argparse.ArgumentParser()
parser.add_argument("-t", default="google",
                    help="set the translator to use. -t deepl for DeepL, -t google for Google Translate, -t openai for OpenAI. Defaults to google. For DeepL must also specify auth key with -a ")
parser.add_argument("-a", default="", help="set auth key to use for DeepL")
parser.add_argument("-f", default="Localizable.strings",
                    help="set the path to the original Localizable.strings to read keys from")
parser.add_argument("-o", default="en",
                    help="set the origin locale for auto translation, default is english")
parser.add_argument("-d", default="", help="For delta translations. Set the path to the root directory where existing localized translations exist. If specified, this path will be used to check if a line / key has already been translated and skip translating that line. This way only the keys that do not exist in the existing destination file will be translated.")
parser.add_argument(
    "-e", default="0", help="emulate only. This will not perform any translation but instead emulate and print out details of strings that would need to be translated.")
parser.add_argument("-v", default="0", help="Verbose")
args = parser.parse_args()


def translate_text_with_openai(text, source_lang, target_lang, context=None):
    openai.api_key = read_open_ai_token()
    prompt = f" Translate the following text from {source_lang} to {target_lang}: {text}."
    adPrompt = f" Your goal is to translate text, but not to change it's meaning. You can use the following context to help you: {context}. All your answers strictly target language. don't add a period at the end and don't capitalize it if it's the original text not with a capital letter"
    if context:
        prompt = f"{adPrompt}\n\n{prompt}"

    if args.v == "2":
        print("---------------------------------------------")
        print("  ..... OpenAI Prompt: %s" % (prompt))
        print("---------------------------------------------")
    # end if

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=1000,
        stream=False,
    )
    if args.v == "2":
        print("---------------------------------------------")
        print("  ..... OpenAI response: %s" % (response))
        print("---------------------------------------------")
    # end if

    if response.choices:
        return response.choices[0].text.strip()
    else:
        return None
    # end if
# end def


def translateSourceText(sourceText, translateTargetCode, context=None):
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
            # end if

            pass

        elif str(args.t).strip().lower() == "openai":
            result = translate_text_with_openai(
                sourceText, "English", target_lang=translateTargetCode, context=context)
            translatedText = result
            if args.v == "1":
                print("  ..... Translated with OpenAI: %s => %s" %
                      (sourceText, translatedText))
            # end if

        elif str(args.t).strip().lower() == "deepl":
            deeplTranslator = deepl.Translator(args.a)
            result = deeplTranslator.translate_text(
                sourceText, source_lang=args.o, target_lang=translateTargetCode)

            translatedText = result.text

            if args.v == "1":
                print("  ..... Translated with DeepL: %s => %s" %
                      (sourceText, translatedText))
            # end if
        else:
            googleTranslator = Translator()
            obj = googleTranslator.translate(
                sourceText, src=args.o, dest=translateTargetCode)

            translatedText = obj.text

            if args.v == "1":
                print("  ..... Translated with Google: %s => %s" %
                      (sourceText, translatedText))
            # end if
        # end if
    except Exception as e:
        print("\n  ..... !! FAILED !! to translate for %s: %s = %s\n" %
              (translateTargetCode, sourceText, e))

        return (sourceText, False, False)
    # end try

    # Deepl can produce translations with double quotes, we need to escape those properly
    translatedText = translatedText.replace('\\N', '\\n')
    translatedText = translatedText.replace('\\"', '"')
    translatedText = translatedText.replace("\"", "\\\"")
    translatedText = translatedText.replace("％", "%")
    translatedText = translatedText.replace("% @", "%@")
    translatedText = translatedText.replace("（", " (")
    translatedText = translatedText.replace("）", ") ")
    translatedText = translatedText.replace("% @", "%@")
    translatedText = translatedText.replace("\\ n", "\n")
    translatedText = translatedText.strip(' ')

    # Some basic validation to confirm translation did not get rid of formatters in source text
    totalFormattersInSource = sourceText.count('%')
    totalFormattersInOutput = translatedText.count('%')

    formatterFailed = False
    if totalFormattersInSource != totalFormattersInOutput:
        formatterFailed = True
        print("\n  ..... !! WARNING !! Formatters don't match in: %s => %s (lang: %s)\n" % (
            sourceText, translatedText, translateTargetCode))
    elif translatedText.count('% ') != sourceText.count('% '):
        formatterFailed = True
        print("\n  ..... !! WARNING !! Formatters have an invalid space: %s => %s (lang: %s)\n" % (
            sourceText, translatedText, translateTargetCode))
    # end if
    percent_index = translatedText.find('%')
    if percent_index != -1 \
            and len(translatedText) > percent_index + 1 \
            and translatedText[translatedText.find('%') + 1] not in ['u', 'l', '@', 'f', '1', '2', '3', 'd', '.']:
        formatterFailed = True

        print("\n  ..... !! WARNING !! Invalid formatter: %s => %s (lang: %s)\n" % (
            sourceText, translatedText, translateTargetCode))
    # end if

    return (translatedText, True, formatterFailed)
# end def


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
        # end if
    # end for

    return True
# end def


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
    # end if

    (translation, success, warning) = translateSourceText(
        sourceText, translateTargetCode, context=stringComment)

    if success:
        # Only save translated lines
        if str(args.e).strip().lower() == "1":
            # Emulating only
            pass
        else:
            writeTranslationToFile(
                stringsFileName, stringName, translation, stringComment, outputTargetCode)
        # end if
    # end if

    return (success, warning)
# end def


def translateFile(stringsFileName, translateFriendlyName, translateTargetCode, outputTargetCode):
    """
    Translate source language for the given target language / output file
    :param stringsFileName: The .strings file name
    :param translateFriendlyName: friendly name for printing
    :param translateTargetCode: google translation target code
    :param outputTargetCode: output target code
    :return:
    """
    print("Translating for: " + translateFriendlyName)
    if len(args.d.strip()) == 0:
        clearContentsOfFile(stringsFileName, outputTargetCode)
    # end if

    # When delta-translating, pre-load existing translations to compare against
    existingOutputTranslations = []
    if len(args.d.strip()) != 0:
        fullExistingPath = os.path.expanduser(args.d.strip())

        pathToExistingFile = os.path.join(
            fullExistingPath, outputTargetCode + os.path.join(".lproj", stringsFileName))

        print("Reading existing Localizable.strings from path: %s" %
              (pathToExistingFile))

        existingOutputTranslations = readTranslations(pathToExistingFile)

        print("  ... will only translate new keys. Existing translations found: %s keys" % (
            len(existingOutputTranslations)))
    # end if

    totalLinesTranslated = 0
    totalLinesNeeded = 0
    totalSkipped = 0
    totalWarnings = 0
    for translationTuple in originLines:
        if translationNeeded(translationTuple, translateTargetCode, existingOutputTranslations):
            totalLinesNeeded += 1

            (success, warning) = translateLineInFile(
                translationTuple, translateTargetCode, outputTargetCode)
            if success:
                totalLinesTranslated += 1
            # end if
            if warning:
                totalWarnings += 1
            # end if
        else:
            totalSkipped += 1
            if args.v == "1":
                print("  ........... skipping already translated key: %s" %
                      (translationTuple['key']))
            # end if
        # end if
    # end for

    if totalWarnings != 0:
        print("ERROR: CHECK WARNINGS. Total reported %s" % (totalWarnings))
    # end if

    if totalLinesNeeded != totalLinesTranslated:
        print("ERROR: NOT ALL LINES TRANSLATED. Total lines translated for %s: %s. Original source count: %s" % (
            translateFriendlyName, totalLinesTranslated, totalLinesNeeded))
    else:
        if len(args.d.strip()) != 0:
            print("SUCCESS: New lines translated for %s: %s, skipped: %s" %
                  (translateFriendlyName, totalLinesTranslated, totalSkipped))
        else:
            print("SUCCESS: Total lines translated for %s: %s" %
                  (translateFriendlyName, totalLinesTranslated))
        # endif
    # end if
# end def


if str(args.t).strip().lower() == "deepl":
    print("Using DeepL translator")
# endif

if str(args.t).strip().lower() == "openai":
    print("Using OpenAI translator")
# endif

# Read and cache origin language once
originPath = os.path.expanduser(args.f.strip())
dirName, stringsFileName = os.path.split(originPath)
print("Reading source language: %s" % (originPath))
print("Will use filename: %s" % (stringsFileName))

originLines = readTranslations(originPath)

print("Total lines in source: %s\n" % (len(originLines)))

with open('LanguageCodes.txt', 'r') as supportedLangCodeFile:
    for targetLine in supportedLangCodeFile:

        if targetLine.strip().startswith("#"):
            continue
        # end if

        targetArray = targetLine.split()
        translateFriendlyName = targetArray[0]
        googleTranslateTargetCode = targetArray[1]
        deeplTranslateTargetCode = targetArray[2]
        outputTargetCode = targetArray[3]

        if deeplTranslateTargetCode.strip() == "-" and str(args.t).strip().lower() == "deepl":
            print("Ignoring non-supported language for DeepL: %s" %
                  (translateFriendlyName))
            continue
        # endif

        useLangCode = googleTranslateTargetCode
        if str(args.t).strip().lower() == "deepl":
            useLangCode = deeplTranslateTargetCode
        # end if

        if str(args.t).strip().lower() == "openai":
            useLangCode = translateFriendlyName
        # end if

        translateFile(stringsFileName, translateFriendlyName,
                      useLangCode, outputTargetCode)

        print("\n")
    # end for
# end def
