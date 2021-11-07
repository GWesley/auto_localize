#!/usr/bin/python3
import re
import os
import os.path
import argparse
import deepl
import codecs, chardet
from googletrans import Translator

parser = argparse.ArgumentParser()
parser.add_argument("-t", default="google", help="set the translator to use. -t deepl for DeepL, -t google for Google Translate. Defaults to google. For DeepL must also specify auth key with -a ")
parser.add_argument("-a", default="", help="set auth key to use for DeepL")
parser.add_argument("-f", default="Localizable.strings", help="set the path to the original Localizable.strings to read keys from")
parser.add_argument("-o", default="en", help="set the origin locale for auto translation, default is english")
parser.add_argument("-d", default="", help="For delta translations. Set the path to the root directory where existing localized translations exist. If specified, this path will be used to check if a line / key has already been translated and skip translating that line. This way only the keys that do not exist in the existing destination file will be translated.")
parser.add_argument("-v", default="1", help="Verbose")
args = parser.parse_args()

format_encoding = 'UTF-16'

def createOutputDirectoryIfNotExists(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))
    #end if
#end def

def _unescape_key(s):
    return s.replace('\\\n', '')
#end def

def _unescape(s):
    s = s.replace('\\\n', '')
    return s.replace('\\"', '"').replace(r'\n', '\n').replace(r'\r', '\r')
#end def

def _get_content_from_file(filename, encoding='UTF-16'):
    f = open(filename, 'rb')
    try:
        content = f.read()
        if chardet.detect(content)['encoding'].startswith(format_encoding):
            #f = f.decode(format_encoding)
            encoding = format_encoding
        else:
            #f = f.decode(default_encoding)
            encoding = 'utf-8'
        f.close()
        f = codecs.open(filename, 'r', encoding=encoding)
        return f.read()
    except IOError as e:
        print("Error opening file %s with encoding %s: %s" %\
                (filename, format_encoding, e.message))
    except Exception as e:
        print("Unhandled exception: %s" % e.message)
    finally:
        f.close()

def readTranslations(fileName):
    """
    Read in a given Localizable.strings file and return a list of key / value pairs read for each line of translation.

    :param fileName:
    :return: List of tuples with key / value pairs of each translation found
    """

    print("Reading Localizable.strings from path: %s" % (fileName))
    if not os.path.exists(fileName):
        print(" ... no file found, returning empty translation")
        return []
    #endif

    readLines = []

    stringset = []
    f = _get_content_from_file(filename=fileName)
    if f.startswith(u'\ufeff'):
        f = f.lstrip(u'\ufeff')
    # regex for finding all comments in a file
    cp = r'(?:/\*(?P<comment>(?:[^*]|(?:\*+[^*/]))*\**)\*/)'
    p = re.compile(
        r'(?:%s[ \t]*[\n]|[\r\n]|[\r]){0,1}(?P<line>(("(?P<key>[^"\\]*(?:\\.[^"\\]*)*)")|(?P<property>\w+))\s*=\s*"(?P<value>[^"\\]*(?:\\.[^"\\]*)*)"\s*;)' % cp,
        re.DOTALL | re.U)
    # c = re.compile(r'\s*/\*(.|\s)*?\*/\s*', re.U)
    c = re.compile(r'//[^\n]*\n|/\*(?:.|[\r\n])*?\*/', re.U)
    ws = re.compile(r'\s+', re.U)
    end = 0
    start = 0
    for i in p.finditer(f):
        start = i.start('line')
        end_ = i.end()
        key = i.group('key')
        comment = i.group('comment') or ''
        if not key:
            key = i.group('property')
        value = i.group('value')
        while end < start:
            m = c.match(f, end, start) or ws.match(f, end, start)
            if not m or m.start() != end:
                print("Invalid syntax: %s" % \
                      f[end:start])
            end = m.end()
        end = end_
        key = _unescape_key(key)
        stringset.append({'key': key, 'value': _unescape(value), 'comment': comment})
    return stringset
#end def

def writeToFile(sourceText, translatedText, outputTargetCode):
    outputFileName = "output/" + outputTargetCode + ".lproj/Localizable.strings"
    with open(outputFileName, "a", encoding="utf-8") as myfile:
        createOutputDirectoryIfNotExists(outputFileName)
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

    translatedText = sourceText

    try:
        if str(args.t).strip().lower() == "deepl":
            deeplTranslator = deepl.Translator(args.a)
            result = deeplTranslator.translate_text(sourceText, source_lang=args.o, target_lang=translateTargetCode)

            translatedText = result.text
        else:
            googleTranslator = Translator()
            obj = googleTranslator.translate(sourceText, src=args.o, dest=translateTargetCode)

            translatedText = obj.text
        #end if
    except Exception as e:
        if args.v == '1':
            print("   FAILED to translate for %s: %s = %s" % (translateTargetCode, sourceText, e))
        #endif
        return (sourceText, False)
    #end try

    # Deepl can produce translations with double quotes, we need to escape those properly
    translatedText = translatedText.replace("\"", "\\\"")

    # Some basic validation to confirm translation did not get rid of formatters in source text
    totalFormattersInSource = sourceText.count('%')
    totalFormattersInOutput = translatedText.count('%')

    if totalFormattersInSource != totalFormattersInOutput:
        print("    WARNING. Formatters don't match in: %s => %s (lang: %s)" % (sourceText, translatedText, translateTargetCode))
    #end if

    return (translatedText, True)
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

    (translation, success) = translateSourceText(sourceText, translateTargetCode)

    if success:
        # Only save translated lines
        writeToFile(stringName, translation, outputTargetCode)
    #end if

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

    # When delta-translating, pre-load existing translations to compare against
    existingOutputTranslations = []
    if len(args.d.strip()) != 0:
        fullExistingPath = os.path.expanduser(args.d.strip())

        pathToExistingFile = fullExistingPath + "/" + outputTargetCode + ".lproj/Localizable.strings"
        existingOutputTranslations = readTranslations(pathToExistingFile)

        print("  ... will only translate new keys. Existing translations found: %s keys" % (len(existingOutputTranslations)))
    #end if

    totalLinesTranslated = 0
    totalLinesNeeded = 0
    for translationTuple in originLines:
        if translationNeeded(translationTuple, translateTargetCode, existingOutputTranslations):
            totalLinesNeeded += 1

            if translateLineInFile(translationTuple, translateTargetCode, outputTargetCode):
                totalLinesTranslated += 1
            #end if
        else:
            if args.v == "1":
                print("  ....... skipping already translated key: %s" % (translationTuple['key']))
            #end if
        #end if
    #end for

    if totalLinesNeeded != totalLinesTranslated:
        print("WARNING: Total lines translated for %s: %s. Original source count: %s" % (translateFriendlyName, totalLinesTranslated, totalLinesNeeded))
    else:
        if len(args.d.strip()) != 0:
            print("SUCCESS: New lines translated for %s: %s" % (translateFriendlyName, totalLinesTranslated))
        else:
            print("SUCCESS: Total lines translated for %s: %s" % (translateFriendlyName, totalLinesTranslated))
        #endif
    #end if
#end def

if str(args.t).strip().lower() == "deepl":
    print("Using DeepL translator")
#endif

# Read and cache origin language once
print("Reading source language: %s" % (args.f))

originLines = readTranslations(args.f)

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

        print("\n\n")
    #end for
#end def


