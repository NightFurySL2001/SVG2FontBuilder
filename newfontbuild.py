from fontTools.fontBuilder import FontBuilder
from fontTools.svgLib import SVGPath
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Scale

from picosvg.svg import SVG as picoSVG

from natsort import os_sorted
from types import SimpleNamespace
import string
import os
import csv
import re
import pathlib
from lxml import etree as ET
# draw a .notdef glyph of 1000x1000
def drawNotdefGlyph(type="bezier", upm=1000, ascender=880):
    if type == "quad":
        ori_pen = TTGlyphPen(None)
    else:
        ori_pen = T2CharStringPen(1000, None)
    t = Scale(upm / 1000).translate(0, ascender * 1000 / upm - 880)
    pen = TransformPen(ori_pen, t)
    pen.moveTo((100, -120))
    pen.lineTo((900, -120))
    pen.lineTo((900, 880))
    pen.lineTo((100, 880))
    pen.lineTo((100, -120))
    pen.closePath()
    pen.moveTo((150, -29))
    pen.lineTo((150, 789))
    pen.lineTo((468, 380))
    pen.lineTo((150, -29))
    pen.closePath()
    pen.moveTo((182, -70))
    pen.lineTo((500, 339))
    pen.lineTo((818, -70))
    pen.lineTo((182, -70))
    pen.closePath()
    pen.moveTo((532, 380))
    pen.lineTo((850, 789))
    pen.lineTo((850, -29))
    pen.lineTo((532, 380))
    pen.closePath()
    pen.moveTo((500, 421))
    pen.lineTo((182, 830))
    pen.lineTo((817, 830))
    pen.lineTo((500, 421))
    pen.closePath()
    if type == "quad":
        return ori_pen.glyph()
    else:
        return ori_pen.getCharString()

def getOutlineFromSVG(svg_fulltext, upm: int, ascender: int, picoNormalize):
    """
    Input a svg string, and reads the glyph into a T2 glyph
    """
    # # if normalize, convert to picoSVG to spec in place
    # if picoNormalize:
    # # read SVG into string
    #     svg_fullstring = open(svg_fullpath, "r", encoding="utf-8-sig").read()
    #     # parse SVG 
    #     picosvg = picoSVG.fromstring(svg_fullstring)
    #     picosvg.topicosvg(inplace=True, allow_text=True)
        
    #     # convert picosvg into svgpen
    #     svgpen = SVGPath(None)
    #     svgpen.root = picosvg.svg_root
        
    #     # get viewbox
    #     xori, yori, width, height = picosvg.view_box()
    # else:
    #     svgpen = SVGPath(filename=svg_fullpath)

    #     # get viewbox
    #     viewBox_string = svgpen.root.attrib["viewBox"].split(" ")
    #     xori, yori, width, height = [float(x) for x in viewBox_string]

    # parse SVG 
    picosvg = picoSVG.fromstring(svg_fulltext)
    # if normalize, convert to picoSVG to spec in place
    if picoNormalize:
        # remove image and style
        # image not supported
        # style not supported for now: https://github.com/googlefonts/picosvg/issues/216
        picoerrors = picosvg.checkpicosvg()
        if picoerrors:
            for i in picoerrors:
                # skip if not image and style, prefilter
                if not re.search(r"/style\[\d+\]$", i) and not re.search(r"/image\[\d+\]$", i):
                    continue

                # remove style and image elements
                for context in picosvg.breadth_first():
                    if re.search(r"/style\[\d+\]$", context.path) or re.search(r"/image\[\d+\]$", context.path):
                        context.element.getparent().remove(context.element)
                break # only need remove once
        picosvg.topicosvg(inplace=True, allow_text=True)
        
    # convert picosvg to svgpath pen
    svgpen = SVGPath(None)
    # carry svg etree root over
    svgpen.root = picosvg.svg_root

    # get viewbox
    xori, yori, width, height = picosvg.view_box()

    scale = upm / height
    # prepare transformation
    move_height = ascender - (yori * -scale)
    t = Scale(scale, -scale).translate(-xori / -scale, move_height / -scale)
    # calculate glyph advance with x coord
    glyphadv = t.transformPoint((width, 0))[0]

    # new pen
    # glyphpen = TTGlyphPen(None)
    glyphpen = T2CharStringPen(glyphadv, None)
    # wrap pen with transform pen
    transformPen = TransformPen(glyphpen, t)
    # draw glyph
    svgpen.draw(transformPen)
    # glyph = glyphpen.glyph()
    glyph = glyphpen.getCharString()
    return (glyph, glyphadv)


def uniName(char):
    num = ord(char[0])
    if num in aglfn_namelist.values():
        name = [key for key, val in aglfn_namelist.items() if val == num][0] # search dict, use first name
    elif num < 65536: # bmp character
        name = "uni" + hex(num).upper()[2:]
    else:
        name = "u" + hex(num).upper()[2:]
    return (name, num)

def uses_other_chars(s):
    return not set(s) <= aglfn_allowedchar

# https://github.com/adobe-type-tools/agl-specification Section 2
def getUniFromAdobeName(name):
    """
    Return a tuple of valid Adobe glyph name based on filename, and its corresponding Unicode codepoint. Return None if filename is not valid.
    If a single Unicode character is inputted as filename, it will be parsed first and return a valid Adobe glyph name or uniXXXX/uXXXXXX.

    input: filename
    output: tuple(valid Adobe glyph name, Unicode codepoint integer or None)
    """
    # length 1, directly encode character (eg 一.svg, ㄅ.svg)
    if len(name.strip()) == 1: 
        return uniName(name)
    # contains invalid Adobe glyph name chars
    if uses_other_chars(name):
        return (re.sub("[^"+"".join(aglfn_allowedchar)+"]", "", name), None)
    # variant glyph names (eg A.smcp, f_i), no unicode
    if "." in name or "_" in name:
        return (name, None)
    # filename is in aglfn predefined list
    if name in aglfn_namelist:
        return (name, aglfn_namelist[name])
    
    # name format "uniXXXX"
    if name.startswith("uni") and len(name.strip()[3:]) == 4:
        try:
            num = int(name[3:7], 16)
            if num in range(0xD800, 0xE001): # UTF-16
                return (name, None)
            return (name, num)
        except ValueError: # not base 16
            return (name, None)
    
    # name format "uXXXXXX"
    if name.startswith("u"):
        if len(name.strip()[1:]) not in (4, 5, 6): # only allow 4-6
            return (name, None)
        try:
            num = int(name.strip()[1:], 16)
            if num in range(0xD800, 0xE001) or num > 0x10FFFF: # UTF-16, out of Unicode
                return (name, None)
            return (name, num)
        except ValueError: # not base 16
            return (name, None)
    # fallback
    return (name, None)

def checkDuplicateName(name, list):
    """
    Check for same name in list and if so, return a new name that is not in the list by appending a number
    """
    if name not in list:
        return name
    i = 0
    tempname = name
    while tempname in list:
        i += 1
        tempname = name + "." + str(i)
    return tempname

def getAllFiles(path):
    fulllist=[]
    for folder, subfolders, files in os.walk(path):
        for file in files:
            filePath = os.path.normpath(os.path.abspath(os.path.join(folder, file)))
            fulllist.append(filePath)
    return fulllist


def build_font(folder, csv_mapping, use_CSV, nameStrings, headVersion, outputFile, metrics=None, vendorCode="", picoNormalize=True, strictMode=True):
    # return log screen when done
    log = ""

    # convert svg filename to Unicode character/glyph name
    filename_char_map = {} 
    if use_CSV:
        with open(csv_mapping, "r", encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                filename = line[0]
                # check if absolute path
                if not os.path.isabs(filename):
                    # join path with svg folder
                    filename = os.path.join(folder, filename)
                filename = os.path.normpath(filename)
                # verify filename
                if filename.lower().endswith(".svg"):
                    filename_char_map[filename] = line[1]
                else:
                    log += line[0] + " in CSV is ignored: not SVG\n"
    
    if metrics is None:
        metrics = dict(
            upm = 1000,
            ascender = 880,
            descender = 120,
            line_gap = 0,
            safe_ascender = 1100,
            safe_descender = 250,
        )
    metrics = SimpleNamespace(**metrics)

    ## START PREPROCESSING SVG

    # glyph order, add default .notdef
    glyphOrder = [".notdef"]
    # unicode mapping
    charmap = {}
    # glyph outline
    glyphs = {}
    glyphs[".notdef"] = drawNotdefGlyph("bezier", metrics.upm, metrics.ascender)
    # glyph advance width
    advanceWidths = {}
    advanceWidths[".notdef"] = 1000

    # loop through svg files, by OS sorting order (os_sorted)
    for filename in os_sorted(getAllFiles(folder)):
        name, ext = os.path.splitext(os.path.basename(filename))
        # check if svg
        if ext.lower() != ".svg":
            log += (f"%s is not a SVG file\n" % (filename))
            continue
        name = name.strip()

        # use CSV mapping
        if use_CSV:
            # strict mode, skip filename with *no* predefined filename-character mapping
            if strictMode and filename not in filename_char_map:
                continue

            # find character that is mapped to filename (with .svg extension), or return name without ".svg"
            new_char_name = filename_char_map.get(filename, name)
            # parse the remapped char name to glyph name
            glyphname, uni = getUniFromAdobeName(new_char_name)
        # check filename
        else:
            # directly parse filename to glyph name
            glyphname, uni = getUniFromAdobeName(name)

        # check if duplicate glyphname, rename if exist
        glyphname = checkDuplicateName(glyphname, glyphOrder)

        # add glyph to glyph order
        glyphOrder.append(glyphname)

        # not None, unicode not assigned before
        if uni is not None and uni not in charmap:
            # assign unicode
            charmap[uni] = glyphname
        elif uni in charmap:
            log += (
                f"Unicode %s is already assigned to glyph name %s\n"
                % ("U+"+hex(uni).upper()[2:], charmap[uni])
            )

        # read SVG into string
        svg_fulltext = open(os.path.join(folder, filename), "r", encoding="utf-8-sig").read()
        # get glyph outline
        glyph, glyphadv = getOutlineFromSVG(svg_fulltext, metrics.upm, metrics.ascender, picoNormalize)
    
        # save glyph into glyphs dict
        glyphs[glyphname] = glyph
        # set glyph advance
        advanceWidths[glyphname] = glyphadv
    
    ## END PREPROCESSING SVG

    # start building
    fb = FontBuilder(metrics.upm, isTTF=False)
    fb.setupGlyphOrder(glyphOrder)
    fb.setupCharacterMap(charmap)

    # for glyf (quadratic)
    # fb.setupGlyf(glyphs)
    # glyphTable = fb.font["glyf"]
    # set metrics
    # horiMetrics = {}
    # for gn, advanceWidth in advanceWidths.items():
    #     horiMetrics[gn] = (advanceWidth, glyphTable[gn].xMin)

    # for CFF (cubic)
    fb.setupCFF(nameStrings["psName"]["en"], {"FullName": nameStrings["psName"]["en"]}, glyphs, {})
    # calculat lsb
    lsb = {gn: cs.calcBounds(None)[0] for gn, cs in glyphs.items()}
    horiMetrics = {}
    for gn, advanceWidth in advanceWidths.items():
        horiMetrics[gn] = (advanceWidth, lsb[gn])

    fb.setupHorizontalMetrics(horiMetrics)
    fb.setupHorizontalHeader(ascent=metrics.safe_ascender, descent=-metrics.safe_descender, lineGap=metrics.line_gap)

    # other font info
    fb.setupNameTable(nameStrings)

    fb.setupOS2(
        sTypoAscender=metrics.ascender,
        sTypoDescender=-metrics.descender,
        sTypoLineGap=metrics.line_gap,
        usWinAscent=metrics.safe_ascender,
        usWinDescent=metrics.safe_descender,
        achVendID=vendorCode,
    )
    fb.setupPost()

    fb.setupHead(fontRevision=headVersion)

    fb.save(outputFile)

    if log == "":
        log = "Font successfully generated!\nFilename: " + outputFile
    return log


global aglfn_allowedchar
aglfn_allowedchar = frozenset(string.ascii_letters + string.digits + '._')
aglfn_namelist = {}
for line in open("aglfn.txt", "r", encoding="utf-8-sig"):
    if line.startswith("#"):
        continue
    uni, name, _ = line.split(";")
    aglfn_namelist[name] = int(uni, 16)

# test build_font functionality in this file
# def build_test():
#     familyName = "My Font"
#     styleName = "Regular"

#     nameStrings = dict(
#         familyName = dict(en=familyName),
#         styleName = dict(en=styleName),
#         typographicFamily = dict(en=familyName),
#         typographicSubfamily = dict(en=styleName),
#         uniqueFontIdentifier = dict(en="SVG2FontBuilder:" + familyName + "." + styleName),
#         fullName = dict(en=familyName + "-" + styleName),
#         psName = dict(en=familyName + "-" + styleName),
#         version="Version 1.000; testing; SVG2FontBuilder",
#     )
#     build_font("test/svgwechat", "", False, nameStrings, 123, "test/test.otf", picoNormalize=True, strictMode=False)
# if __name__ == "__main__":
#     build_test()