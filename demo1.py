#! /usr/bin/env python
import cairo
import math
import sys


STEP = None

ALIGN_BOTTOM = 1
ALIGN_CENTER = 2

class Diagram(object):

    def __init__(self, filename, nActors, nMessages, pixWidth):
        global STEP

        nxTiles = 4 * nActors
        STEP = 1.0 * pixWidth / nxTiles
        width = pixWidth;
        nyTiles = nMessages * 2
        height = nyTiles * STEP

        print "width=", width, ", height=", height, ", STEP=", STEP

        self.surface = cairo.SVGSurface(filename + '.svg', width, height)
        cr = self.cr = cairo.Context(self.surface)

        #cr.scale(width/100.0, height/100.0)
        cr.set_line_width(STEP/40)

        # draw white background
        cr.rectangle(0, 0, width, height)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()

        self.draw_dest()

        cr.set_line_width( max(cr.device_to_user_distance(2, 2)) )
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, width, height)
        cr.stroke()

        self.surface.write_to_png(filename + '.png')
        cr.show_page()
        self.surface.finish()

    def init(self):
        self.cr.set_source_rgba(0, 0, 0)
        self.cr.set_line_width(STEP/40)
        self.cr.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    def dot(self, x, y):

        self.cr.arc(x, y, STEP/20, 0, 2 * math.pi)
        self.cr.fill()


    def boxWithLifeLine(self, x, y, text):
        
        self.box(x, y, text)

        BOX_HEIGHT = STEP * 1
        # the life line
        y0 = y + BOX_HEIGHT/2
        self.cr.move_to(x, y0)
        self.cr.line_to(x, y0 + BOX_HEIGHT/2)
        self.cr.stroke()


    def box(self, x, y, text):
        """Draw a box around (x, y), with centered text."""

        #self.dot(x, y)

        # the box
        width = w = STEP * 2
        height = h = STEP * 1

        self.cr.rectangle(x-w/2, y-h/2, w, h)
        self.cr.stroke()

        # the text
        self.text(x, y, text)

        # the starting life-line
    
    def lifeLine(self, x, y0, y1):

        self.cr.move_to(x, y0)
        self.cr.line_to(x, y1)
        self.cr.stroke()

    def text(self, x, y, text, flags = ALIGN_CENTER):
        """Write some text centered on (x, y)."""
        self.cr.set_font_size(STEP/4)
        fascent, fdescent, fheight, fxadvance, fyadvance = self.cr.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = self.cr.text_extents(text)

        xRef = x - width / 2

        if flags == ALIGN_BOTTOM:
            yRef = y - height / 2
        else: # centered
            yRef = y + fdescent

        self.cr.move_to(xRef, yRef)
        self.cr.show_text(text)

    def arrow(self, x0, y0, x1, y1, text):

        print "arrow(", x0, y0, x1, y1, ")"

        if x1 == x0:
            print "error, arrow"
            return

        elif x1 < x0:
            sign = -1 # indicate that the arrow is from right to left

        else:
            sign = 1

        angle = math.atan((y1-y0)/(x1-x0))

        print "angle=", angle
        size = math.sqrt((y1-y0)**2 + (x1-x0)**2)

        self.cr.save()

        self.cr.translate(x0, y0)

        # a small dot for the starting point of the arrow
        self.dot(0, 0)

        self.cr.rotate(angle)

        # the main line of the arrow
        self.cr.move_to(0, 0)
        xHead = size * sign

        self.cr.line_to(xHead, 0)
        self.cr.stroke()

        # head of the arrow
        yHead = 0
        arrowSize = STEP/4 # hypothenuse
        hAngle = math.pi / 6
        x2 = xHead - arrowSize * math.cos(hAngle) * sign
        y2 = yHead - arrowSize * math.sin(hAngle)
        self.cr.move_to(xHead, yHead)
        self.cr.line_to(x2, y2)
        self.cr.move_to(xHead, yHead)
        x3 = xHead - arrowSize * math.cos(hAngle) * sign
        y3 = yHead + arrowSize * math.sin(hAngle)
        self.cr.line_to(x3, y3)
        self.cr.stroke()
        

        # text
        x = xHead / 2
        y = 0
        self.text(x, y, text, ALIGN_BOTTOM)

        self.cr.restore()


class Demo1(Diagram):
    def draw_dest(self):

        self.init()

        # Bob
        BOB = STEP * 2
        self.boxWithLifeLine(BOB, STEP, "Bob")
        self.lifeLine(BOB, STEP * 2, STEP * 9)

        # Alice
        ALICE = STEP * 5
        self.boxWithLifeLine(ALICE, STEP, "Alice")
        self.lifeLine(ALICE, STEP * 2, STEP * 9)

        TIME = STEP * 3
        # Bob says "hello" to Alice
        self.arrow(BOB, TIME, ALICE, TIME, "hello")
        TIME += STEP
        self.arrow(ALICE, TIME, BOB, TIME, "hi, what's up?")
        TIME += STEP
        self.arrow(BOB, TIME, ALICE, TIME+STEP, "it's rainy today")
        TIME += STEP

class Demo2(Diagram):
    def draw_dest(self):

        self.init()

        # Host1
        HOST1 = STEP * 2
        self.boxWithLifeLine(HOST1, STEP, "Host 1")
        self.lifeLine(HOST1, STEP * 2, STEP * 9)

        # Example.com
        EXAMPLE_COM = STEP * 7
        self.boxWithLifeLine(EXAMPLE_COM, STEP, "example.com")
        self.lifeLine(EXAMPLE_COM, STEP * 2, STEP * 9)

        TIME = STEP * 2
        self.arrow(HOST1, TIME, EXAMPLE_COM, TIME+STEP*2, "seq=23")
        TIME += STEP
        TIME += STEP
        self.arrow(HOST1, TIME, EXAMPLE_COM, TIME+STEP*2, "seq=24")
        self.arrow(EXAMPLE_COM, TIME+STEP, HOST1, TIME+STEP*3, "ack=23")
        TIME += STEP
        TIME += STEP
        self.arrow(EXAMPLE_COM, TIME+STEP, HOST1, TIME+STEP*3, "ack=24")
        self.arrow(HOST1, TIME, EXAMPLE_COM, TIME+STEP*2, "seq=25")

        TIME += STEP



if __name__ == '__main__':
    pixWidth = 600
    if len(sys.argv) > 1:
        arg = sys.argv[1]

    else:
        arg = 'demo1'

    if arg == 'demo1': Demo1('demo1', 2, 5, pixWidth)
    elif arg == 'demo2': Demo2('demo2', 3, 10, pixWidth)
