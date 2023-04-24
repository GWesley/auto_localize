#!/usr/bin/python3
import chardet
import codecs
import os
import os.path
import re
import shutil

format_encoding = 'UTF-16'

def readTranslations(fileName):
    """
    Read in a given Localizable.strings file and return a list of key / value pairs read for each line of translation.

    :param fileName:
    :return: List of tuples with key / value pairs of each translation found
    """

    #print("Reading Localizable.strings from path: %s" % (fileName))
    if not os.path.exists(fileName):
        print(" ... no file found, returning empty translation")
        return []
    #endif

    stringset = []
    f = _get_content_from_file(filename=fileName)
    if f.startswith(u'\ufeff'):
        f = f.lstrip(u'\ufeff')
    #end if
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
        # print("Line: %s" % i)
        start = i.start('line')
        end_ = i.end()
        key = i.group('key')
        comment = i.group('comment') or ''

        if not key:
            key = i.group('property')
        #end if

        value = i.group('value')
        while end < start:
            m = c.match(f, end, start) or ws.match(f, end, start)
            if not m or m.start() != end:
                print("Invalid syntax: %s" % f[end:start])
            #end if
            end = m.end()
        #end while
        end = end_
        #key = _unescape_key(key)
        # print("Found key: %s, value: %s, comment: %s" % (key, value, comment))
        stringset.append({'key': key, 'value': value, 'comment': comment})
    return stringset
#end def

def _unescape_key(s):
    return s.replace('\\\n', '')
#end def

def _unescape(s):
    return _unescape_key(s)
    # s = s.replace('\\\n', '')
    # return s.replace('\\"', '"').replace(r'\n', '\n').replace(r'\r', '\r')
#end def

def _get_content_from_file(filename, format_encoding='UTF-16'):
    f = open(filename, 'rb')
    try:
        content = f.read()
        detected_encoding = chardet.detect(content)['encoding']
        if detected_encoding and detected_encoding.startswith(format_encoding):
            encoding = format_encoding
        else:
            encoding = 'utf-8'
        f.close()
        f = codecs.open(filename, 'r', encoding=encoding)
        print("Opening file with detected encoding: %s, with format encoding: %s, with encoding: %s" % (detected_encoding, format_encoding, encoding))
        return f.read()
    except IOError as e:
        print("Error opening file %s with encoding %s: %s" % (filename, format_encoding, e.message))
    except Exception as e:
        print("Unhandled exception: %s" % e.message)
    finally:
        f.close()
    #end try
#end def

def createOutputDirectoryIfNotExists(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))
    #end if
#end def

def writeCommentToFile(stringsFileName, comment, outputTargetCode):
    outputFileName = os.path.join("output", outputTargetCode + os.path.join(".lproj", stringsFileName))

    with open(outputFileName, "a", encoding="utf-8") as myfile:
        createOutputDirectoryIfNotExists(outputFileName)
        contentToWrite = "/* " + comment.strip() + " */\n\n"
        myfile.write(contentToWrite)
    #end with
#end def

def writeTranslationToFile(stringsFileName, sourceText, translatedText, comment, outputTargetCode):
    outputFileName = os.path.join("output", outputTargetCode + os.path.join(".lproj", stringsFileName))

    with open(outputFileName, "a", encoding="utf-8") as myfile:
        createOutputDirectoryIfNotExists(outputFileName)
        contentToWrite = ""
        if len(comment) != 0:
            contentToWrite = "/* " + comment.strip() + " */\n"
        #end if
        contentToWrite += "\"" + sourceText + "\" = \"" + translatedText + "\";\n\n"
        myfile.write(contentToWrite)
    #end with
#end def

def clearContentsOfFile(stringsFileName, target):
    fileName = os.path.join("output", target + os.path.join(".lproj", stringsFileName))

    createOutputDirectoryIfNotExists(fileName)
    open(fileName, 'w').close()
#end def

# not used
def copy_files():
    src_dir = './output'
    dest_dir = '../app/Male\ Sexual\ Energy'
    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file)
        dest_file = os.path.join(dest_dir, file)
        if os.path.exists(dest_file):
            os.remove(dest_file)
        shutil.copy(src_file, dest_dir)
    print("All files from './output' have been copied and replaced to '../app' directory.")

def read_open_ai_token():
    with open('openai_token.txt', 'r') as myfile:
        return myfile.read().replace('\n', '')
    #end with
#end def
