#!/usr/bin/env python3
# Generates small flyers for inviting people to events at the hackerspace.

import argparse
import datetime
import os
import re
import sys
import urllib

from dateutil.parser import parse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Dots per millimeter
A4_MM = [210, 297]
CWD = os.path.dirname(os.path.realpath(__file__))
DATE_TODAY_ISO = datetime.date.today()
FONT_NAME = "Latin Modern Mono Prop"
FONT_DIR = f'{CWD}/ttf'
FONT_FILE = 'lmmono10regular.ttf'
FONT_PATH = f'{FONT_DIR}/{FONT_FILE}'
FONT_URL = f'https://github.com/dworktg/latin-modern-mono-10/blob/master/fonts/{FONT_FILE}?raw=true'
FONT_SIZE = 11.5
PDF_FILE = f'{DATE_TODAY_ISO}-flyer.pdf'
PDF_DIR = f'{CWD}/out'
PDF_PATH = f'{PDF_DIR}/{PDF_FILE}'
COLOR_FONT = (1, 1, 1)
COLOR_FONT_PREVIEW = (.95, .7, 0)
COLOR_BG = (0, 0, 0)
DATE_FORMAT = '%d.%m.%Y, %H:%M'
CROP_MARK_LENGTH = 2 * cm
BORDER_H = .5 * cm
BORDER_V = BORDER_H
GRID_H = 2
GRID_V = 9
PADDING_H = -0.1 * cm
PADDING_V = -0.1 * cm
TEXT_MAX_COLS = 40
TEXT_MAX_LINES = 6
TEXT_INVITATION_FRONT = '''\
  .-==-,     .-==-,     Einladung zu {event_type}
,"     \_  ,"     \_
|  flip  | |  dot   |     {event_title}
`.      ,' `.      ,'
  `"--"'     `"--"'     {event_datetime_reparsed}
   ccc erfa kassel      flipdot.org\
'''


def get_args():
    parser = argparse.ArgumentParser(description='Generates small flyers for inviting people to events at the hackerspace.')
    parser.add_argument('--title', dest='event_title', type=str, required=True,
                        help="event\'s title")
    parser.add_argument('--description', dest='event_description', type=str, required=True,
                        help=f"multiline description of text (max {TEXT_MAX_COLS} cols, {TEXT_MAX_LINES} lines)")
    parser.add_argument('--datetime', dest='event_datetime', type=str, required=True,
                        help="event's date and time; most formats are parsable")
    parser.add_argument('--type', dest='event_type', type=str,
                        help="event's type")
    parser.add_argument('--pages', dest='number_pages', type=int, default=1,
                        help="number of pages")
    parser.add_argument('--preview', dest='preview', action='store_true',
                        help="show preview of single invitation in flipdot yellow™")
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help="increase verbosity of output to debugging")
    parser.add_argument('--no-cropmarks', dest='crop_marks', action='store_false',
                        help="disable drawing crop marks")
    return parser.parse_args()


def debug(args, msg):
    if args.verbose:
        print(msg)


def init_font():
    # Check for font directory
    if not os.path.isdir(FONT_DIR):
        os.mkdir(FONT_DIR)
    # Check for font
    if not os.path.isfile(FONT_PATH):
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    # Register font for use in PDF
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


def get_text_invitation_front(event_title, event_datetime, event_type='Workshop'):
    event_datetime_reparsed = datetime.datetime.strftime(parse(event_datetime), DATE_FORMAT)
    return TEXT_INVITATION_FRONT.format(
        event_type=event_type,
        event_title=event_title,
        event_datetime_reparsed=event_datetime_reparsed,
    )


def draw_bg(c:canvas.Canvas, color):
    path = c.beginPath()
    path.moveTo(0, 0)
    path.lineTo(0, 30 * cm)
    path.lineTo(25 * cm, 30 * cm)
    path.lineTo(25 * cm, 0)
    c.setFillColor(color)
    c.drawPath(path, True, True)


def draw_text_front(x, y, c:canvas.Canvas, args, color):
    c.setFillColor(color)
    for i, line in enumerate(get_text_invitation_front(args.event_title, args.event_datetime, args.event_type).split('\n')[::-1]):
        debug(args, f'front{x} {y} {i * FONT_SIZE}')
        c.drawString(x, y + i * FONT_SIZE, line)


def draw_text_back(x, y, c:canvas.Canvas, args, color):
    lines_pre = re.split('\n|\\n|\\\\n', args.event_description)
    lines = []
    for line_pre in lines_pre:
        if len(line_pre) > TEXT_MAX_COLS:
            # TODO Use re.split for line breaks between words
            line_pre_split = [line_pre[i:i + TEXT_MAX_COLS] for i in range(0, len(line_pre), TEXT_MAX_COLS)]
            for line in line_pre_split:
                lines.append(line)
        else:
            lines.append(line_pre)
    if len(lines) > TEXT_MAX_LINES:
        print(f"Too much text (x / {len(lines)} > {TEXT_MAX_COLS} / {TEXT_MAX_LINES}))")
        sys.exit(1)
    c.setFillColor(color)
    while len(lines) < TEXT_MAX_LINES:
        if len(lines) % 2 == 1:
            lines.append('')
        else:
            lines.insert(0, '')
    for i, line in enumerate(lines[::-1]):
        debug(args, f'back {x} {y} {i * FONT_SIZE}')
        c.drawString(x, y + i * FONT_SIZE, line)


def draw_crop_mark_cross(x, y, c:canvas.Canvas, color):
    draw_crop_mark_h(x, y, c, color)
    draw_crop_mark_v(x, y, c, color)


def draw_crop_mark_v(x, y, c:canvas.Canvas, color):
    c.setLineWidth(.1)
    c.setStrokeColor(color)
    p = c.beginPath()
    p.moveTo(x, y - CROP_MARK_LENGTH / 2)
    p.lineTo(x, y + CROP_MARK_LENGTH / 2)
    c.drawPath(p, stroke=1, fill=0)


def draw_crop_mark_h(x, y, c:canvas.Canvas, color):
    c.setLineWidth(.1)
    c.setStrokeColor(color)
    p = c.beginPath()
    p.moveTo(x - CROP_MARK_LENGTH / 2, y)
    p.lineTo(x + CROP_MARK_LENGTH / 2, y)
    c.drawPath(p, stroke=1, fill=0)


def make_pdf_file(output_filename, args):
    # Check for PDF directory
    if not os.path.isdir(PDF_DIR):
        os.mkdir(PDF_DIR)

    # Jumble up the layout
    title = output_filename
    c = canvas.Canvas(output_filename, pagesize=A4)
    box_width = A4[0] / GRID_H
    box_height = A4[1] / GRID_V
    for pn in range(0, args.number_pages * 2):
        c.setFont(FONT_NAME, FONT_SIZE)
        color_fg = COLOR_FONT
        color_bg = COLOR_BG
        if pn % 2 == 0:
            # Draw front
            draw_bg(c, color_bg)
            for y in range(0, GRID_V):
                for x in range(0, GRID_H):
                    draw_text_front(x * box_width + BORDER_H, y * box_height + BORDER_V, c, args, color_fg)
        else:
            # Draw back
            color_fg = COLOR_BG
            color_bg = COLOR_FONT
            draw_bg(c, color_bg)
            for y in range(0, GRID_V):
                for x in range(0, GRID_H):
                    # TODO Maybe center text horizontally?
                    draw_text_back(x * box_width + BORDER_H, y * box_height + BORDER_V, c, args, color_fg)
        if args.crop_marks:
            # Draw crop marks
            for j in range(0, GRID_V + 1):
                for i in range(0, GRID_H + 1):
                    x = (i * box_width) + PADDING_H + (i / GRID_H * PADDING_H * -2)
                    y = (j * box_height) + PADDING_V + (j / GRID_V * PADDING_V * -2)
                    draw_crop_mark_cross(x, y, c, color_fg)
        c.showPage()
    c.save()


if __name__ == "__main__":
    args = get_args()
    # Optionally use preview yellow
    if args.preview:
        COLOR_FONT = COLOR_FONT_PREVIEW
    init_font()
    make_pdf_file(PDF_PATH, args)
    print(PDF_PATH)
