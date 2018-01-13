"""
ChainAnimations.py

a collection of possible LED chain animations.

These are just examples you may use. You can add your own here and remove any that are never used.

To use them you do something like this in your main.py:-

DAF_D_SEQ= AnimSequence.AnimSequence([
    ChainAnimations.Collider(duration=5, speed=0.1, palette=Palette.RGB, fps=FPS),
    ChainAnimations.FadeIn(duration=5, speed=1, palette=Palette.RGB, fps=FPS),
    ChainAnimations.Wait(duration=6, speed=0.5, palette=Palette.RED, fps=FPS),
    ChainAnimations.WipeRight(duration= 10, speed=1, palette=Palette.RGB, fps=FPS)
])


"""
import time
import random
from LEDAnimator.Colors import *

from ChainAnimBase import ChainAnimBase

# SPARKLE

class Sparkle(ChainAnimBase):
    """
    randomly selects a color from the supplied palette and uses it to color a random pixel at a random brightness
    """
    def __init__(self,**kwargs):
        super(Sparkle,self).__init__(**kwargs)

    def reset(self,**kwargs):
        super(Sparkle, self).reset(**kwargs)

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        for p in range(self.chain.getLength()):
            color=self.palette.getRandomEntry().getPixelColor()
            self.chain.setPixel(p,color)
            factor=random.randint(0,10)/10.0
            self.chain.setPixelBrightness(p,factor)

        self.refreshCanvas()

# SPARKLE-RANDOM
class SparkleRandom(ChainAnimBase):
    """
    Same as SPARKLE but selects a random color - palette is ignored
    """
    def __init__(self,**kwargs):
        super(SparkleRandom,self).__init__(**kwargs)

    def reset(self,**kwargs):
        super(SparkleRandom,self).reset(**kwargs)

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        self.chain.setAllPixelsRandom()

        self.refreshCanvas()

# COMET - a single comet heading left or right
# used by CometRight and CometLeft
class Comet(ChainAnimBase):
    """
    comet is a sequence of pixel which tail off in brightness

    By default the comet is monochrome and uses the first color in the palette for the first session then
    selects the next color for the next session and so on.

    If multiColored is selected it selects the colors from the palette to fill the comet. The palette is reused cyclically

    """
    tailLen=None         # none means use the palette size for the tail length
    direction=1          # low to high (left to right)
    multiColored=False  # if true uses the entire palette otherwise picks one color

    def __init__(self,**kwargs):
        super(Comet,self).__init__(**kwargs)
        self.init=True  # next step intialises the pattern

    def setTailLength(self,length):
        self.tailLen=length

    def reset(self,**kwargs):
        super(Comet,self).reset(**kwargs)
        self.init=True

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        if self.init:
            if self.tailLen is None: self.tailLen=self.palette.getLength()

            # draw the initial pattern - just one comet
            self.chain.setAllPixels(Black.getPixelColor(alpha=0)) # transparent
            c = self.getNextPaletteEntry()  # color to use if not multicolored

            for p in xrange(self.tailLen):
                if self.multiColored: c = self.getNextPaletteEntry()
                brightness = float(p) / self.tailLen

                if self.direction<0: brightness = 1.0-brightness
                self.chain.setPixel(p,c.getPixelColor(brightness=brightness,alpha=brightness))
            self.init = False


        self.refreshCanvas()
        self.chain.roll(self.direction)

# COMET-RIGHT
class CometRight(Comet):
    def __init__(self,**kwargs):
        super(CometRight, self).__init__(**kwargs)
        self.direction = 1

# COMET-LEFT
class CometLeft(Comet):
    def __init__(self,**kwargs):
        super(CometLeft, self).__init__(**kwargs)
        self.direction = -1

# COMETS - repeating pattern of commets head to tail
# length of tail is determined by number of entries in the palette
class Comets(ChainAnimBase):
    """
    Comets is the same as comet but the chain is filled nose to tail
    """
    direction=1
    multiColored=False # use first entry then next etc
    tailLen=None        # use the palette length

    def __init__(self,**kwargs):
        super(Comets,self).__init__(**kwargs)

    def reset(self,**kwargs):
        super(Comets,self).reset(**kwargs)

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        chainLen=self.chain.getLength()

        if self.init:
            if self.tailLen is None: self.tailLen = self.palette.getLength()

            # draw the initial patterns
            self.chain.setChainBrightness(1.0)
            c = self.getNextPaletteEntry()
            for p in xrange(chainLen):
                if self.multiColored: c = self.getNextPaletteEntry()
                # head of the comet is brightest
                brightness = float(p % self.tailLen) / self.tailLen
                if self.direction<0: brightness=1.0-brightness
                # comets become transparent as they fade
                self.chain.setPixel(p, c.getPixelColor(brightness=brightness,alpha=brightness))

            self.init=False

        self.chain.roll(self.direction)
        self.refreshCanvas()

class CometsRight(Comets):
    def __init__(self,**kwargs):
        super(CometsRight, self).__init__(**kwargs)
        self.direction=1

class CometsLeft(Comets):
    def __init__(self,**kwargs):
        super(CometsLeft, self).__init__(**kwargs)
        self.direction=-1

# PULSE - similar to fade in/out but no fading
# uses a 25% duty cycle
# each pulse uses the next color from the palette
# cycling through
class Pulse(ChainAnimBase):
    # use a square wave duty cycle
    # to turn LEDS on or Off

    duty=25

    def __init__(self,**kwargs):
        super(Pulse,self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(Pulse,self).reset(**kwargs)
        self.ledsOn = False  # leds currently off

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        # TODO could we use  if tick % fps*(100/duty)
        # self.tick ranges 0 to (fps-1)
        # turn the LEDS on for 25% of the time
        #if self.tick < int(self.fps/(100.0/self.duty)):
        #    Mark=True
        #else:
        #    Mark=False

        Mark=True if (self.tick % self.fps*100/self.duty)==0 else False

        # self.ledsOn saves us doing running the code when we don't
        # need to
        if Mark and not self.ledsOn:
            self.chain.setAllPixels(self.getNextPaletteEntry().getPixelColor())
            self.ledsOn=True
        elif not Mark and self.ledsOn:
            self.chain.setAllPixels(Black.getPixelColor())
            self.ledsOn=False

        self.refreshCanvas()

# ALT-ON-OFF
# if palette contains only one color then Alt color is black
# otherwise first two colors are used
class AltOnOff(ChainAnimBase):

    def __init__(self,**kwargs):
        super(AltOnOff,self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(AltOnOff,self).reset(**kwargs)

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        # get first color
        color1=self.palette.getEntry(0).getPixelColor()

        # use black as the alternate color if only one palette entry
        if self.palette.getLength()<2:
            color2=Black.getPixelColor()
        else:
            color2=self.palette.getEntry(1).getPixelColor()

        chainLen=self.chain.getLength()

        if self.init:
            self.init=False
            # populate the chain
            for p in range(0,chainLen):
                x,y=self.chain.getPixelXY(p)
                if p%2:
                    self.chain.setPixel(p,color1)
                else:
                    self.chain.setPixel(p,color2)

        self.refreshCanvas()
        self.chain.roll(1)

# ON - uses the palette to color LEDS
# if the color is black the LEDs will be off
class On(ChainAnimBase):

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        if self.init:
            self.chain.setAllPixels(self.getNextPaletteEntry().getPixelColor())
            self.init=False

        # the animation does nothing else
        # it leaves the LEDs on as initialised
        self.refreshCanvas()

#############################################################
#
# fade animations
#
#############################################################

class Fade(ChainAnimBase):
    """
    Fade is the base class for FadeIn,FadeOut and FadeInOut
    """

    direction=1 # fade in by default
    brightness=0       # current brightnessinance
    c=None

    def __init__(self,**kwargs):
        super(Fade,self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(Fade,self).reset(**kwargs)
        self.init=True

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        if self.init:
            self.c=self.getNextPaletteEntry().getPixelColor()
            self.chain.setAllPixels(self.c)
            self.brightness=0.0 if self.direction>0 else 1.0
            self.init=False
        else:
            '''
            self.tick is the current tick within a 1 second window
            there will be fps ticks per second so fps*duration ticks in all
            '''
            self.brightness=float(self.tick)/(self.fps)
            if self.direction>0:
                if self.brightness>=1.0: self.brightness=1.0
            elif self.direction<0:
                self.brightness=1.0-self.brightness
                if self.brightness<=0:   self.brightness=0

        self.chain.setChainBrightness(self.brightness)
        self.refreshCanvas()

class FadeIn(Fade):

    direction=1

    def __init__(self,**kwargs):
        super(FadeIn, self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(FadeIn,self).reset(**kwargs)

class FadeOut(Fade):
    direction = -1

    def __init__(self, **kwargs):
        super(FadeOut, self).__init__(**kwargs)
        self.reset()

    def reset(self, **kwargs):
        super(FadeOut, self).reset(**kwargs)

# FADE-IN-OUT
class FadeInOut(Fade):

    direction=1 # initial is to fade in

    def __init__(self,**kwargs):
        super(FadeInOut, self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(FadeInOut,self).reset(**kwargs)
        self.brightness = 0
        self.direction=True # True=fade in, False=Fadeout
        self.init=True

    def step(self):
        super(FadeInOut,self).step()

        if self.brightness==0 and self.direction<0:
            self.direction=1
            self.init=True
        if self.brightness>=1.0 and self.direction>0:
            self.direction=-1
            self.init=True


# WAIT - does nothing but wait
class Wait(ChainAnimBase):
    def _init__(self,**kwargs):
        super(Wait,self).__init__(**kwargs)

    def reset(self,**kwargs):
        super(Wait,self).reset(**kwargs)

    def step(self):
        pass

# Larson scanner - same as Knight Rider car (ish)
class Larson(ChainAnimBase):

    # user parameters
    larsonSize=2                # half the chain length
    larsonLen=0
    larsonBackground=(0,0,0,0)  # transparent black

    def _init__(self,**kwargs):
        super(Larson,self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(Larson,self).reset(**kwargs)

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        if self.init:
            # setup the Larson
            c = self.getNextPaletteEntry()
            self.chainLen=self.chain.getLength()
            self.larsonLen=int(self.chainLen/self.larsonSize)
            # TODO not really needed??
            self.chain.setAllPixels(Black.getPixelColor(alpha=0)) # transparent background

            for p in range(self.larsonLen/2+1):
                #
                brightness=2*float(p)/self.larsonLen
                # print("Larson brightness p=",p,"brightness=",brightness)
                # as the brightness drops the opacity also drops
                color=c.getPixelColor(brightness=brightness,alpha=brightness)
                self.chain.setPixel(p,color)
                self.chain.setPixel(self.larsonLen-p, color)
            self.refreshCanvas()
            self.position=0
            self.direction=True # move right
            self.init=False
            return

        else:
            if self.direction and self.position<(self.chainLen-self.larsonLen):
                self.chain.shiftRight(fill=None)
                self.position=self.position + 1
            elif self.direction and self.position>=(self.chainLen-self.larsonLen):
                self.chain.shiftLeft(fill=None)
                self.position = self.position - 1
                self.direction=False
            elif not self.direction and self.position==0:
                self.chain.shiftRight(fill=None)
                self.position = self.position + 1
                self.direction=True
            elif not self.direction and self.position>0:
                self.chain.shiftLeft(fill=None)
                self.position = self.position - 1

        self.refreshCanvas()

class KnightRider(Larson):
    def __init__(self,**kwargs):
        super(KnightRider,self).__init__(**kwargs)

# COLLIDER - comets come in from both ends
# and smash in the middle
class Collider(ChainAnimBase):
    fading=False    # when the collision happens change to True
    chainPos=0
    collided=False  # set when the collision has happened
    tailLen=5

    def __init__(self,**kwargs):
        super(Collider, self).__init__(**kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(Collider, self).reset(**kwargs)
        self.init = True
        self.fading=False
        self.chainPos=0
        self.collided=False

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        if self.init:
            self.collided=False
            self.brightness=1.0
            self.fading=False
            self.chain.setAllPixels(Black.getPixelColor(alpha=0))  # all transparent
            self.chain.setChainBrightness(1.0)
            self.chain.setChainAlpha(1.0)       # must start visible for colliding comets
            c = self.getNextPaletteEntry()      # color switch on restart

            # draw the left comet
            for p in xrange(self.tailLen):
                # head of the comet is brightest
                brightness = float(p) / self.tailLen
                self.chain.setPixel(p, c.getPixelColor(brightness=brightness,alpha=brightness))

            # right hand comet
            chainLen=self.chain.getLength()
            self.chainMiddle = int(chainLen / 2)

            for p in xrange(self.tailLen):
                # head of the comet is brightest
                brightness = float(p) / self.tailLen
                self.chain.setPixel(chainLen-p-1, c.getPixelColor(brightness=brightness,alpha=brightness))

            self.chainPos=self.tailLen  # remember comet has a tail
            self.init = False
            return

        if self.collided:
            if self.fading:
                if self.brightness<=0:
                    self.reset()
                    return
                self.chain.setChainBrightness(self.brightness)
                self.chain.setChainAlpha(self.brightness)
                self.brightness-=0.1
            else:
                # collided - create white flash
                self.brightness = 1.0
                self.chain.setChainAlpha(1.0)
                self.chain.setAllPixels(White.getPixelColor(brightness=self.brightness, alpha=1))  # white flash
                self.chain.setChainBrightness(self.brightness)
                self.fading = True
        else:
            # shift the pixels in from both ends until collided
            if self.chainPos>=(self.chain.getLength()/2):
                # white flash
                self.collided=True
            else:
                if self.collided: return
                self.chain.shiftIn(fill=None)
                self.chainPos += 1

        self.refreshCanvas()



####################################################
#
# WIPE animations
#
####################################################
#WIPE-IN - color fills for both ends to middle
class WipeIn(ChainAnimBase):
    """
    color fills from both ends to middle
    """
    c=None          # current color being used

    def __init__(self,  **kwargs):
        super(WipeIn, self).__init__( **kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(WipeIn, self).reset(**kwargs)
        self.init = True

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        self.chainLen = self.chain.getLength()
        self.chainMiddle = int(self.chainLen / 2)

        if self.init:
            if self.c:
                self.chain.setAllPixels(self.c.getPixelColor())
            else:
                self.chain.setAllPixels(Black.getPixelColor())

            self.chain.setChainBrightness(1.0)
            self.c = self.getNextPaletteEntry()
            self.chainPos = 0
            self.init = False

        self.chain.shiftIn(1,self.c.getPixelColor())

        self.chainPos = self.chainPos + 1
        if self.chainPos==self.chainMiddle:
            self.init=True

        self.refreshCanvas()


class WipeOut(ChainAnimBase):
    """
    color fills middle to ends
    """
    c=None # current color being used for fill

    def __init__(self, **kwargs):
        super(WipeOut, self).__init__( **kwargs)
        self.reset()

    def reset(self,**kwargs):
        super(WipeOut, self).reset(**kwargs)
        self.init = True

    def step(self, chain=None):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        self.chainLen = self.chain.getLength()
        self.chainMiddle = int(self.chainLen / 2)

        if self.init:
            if self.c:
                self.chain.setAllPixels( self.c.getPixelColor())
            else:
                self.chain.setAllPixels(Black.getPixelColor())

            self.chain.setChainBrightness(1.0)
            self.c = self.getNextPaletteEntry()
            self.chainPos = self.chainMiddle
            self.init = False

        self.chain.shiftOut(1,self.c.getPixelColor())

        self.chainPos=self.chainPos-1
        if self.chainPos == 0:
            self.init=True

        self.refreshCanvas()

#TODO bug in wipe - orphaned pixel at left

class Wipe(ChainAnimBase):
    """
    Wipe is the base class for WipeLeft and WipeRight

    if direction==True the wipe is to the right and if False it is to the left

    """
    c=None          # current color
    direction=True  # default is wipe right
    chainLen=0
    multiColored=False

    def __init__(self, **kwargs):
        super(Wipe, self).__init__( **kwargs)
        self.direction=True # wipe right
        self.reset()

    def reset(self,**kwargs):
        super(Wipe, self).reset(**kwargs)
        self.init = True

    def step(self):
        if self.isNotNextStep():
            self.refreshCanvas()
            return

        self.chainLen = self.chain.getLength()

        if self.init:
            # initially clear everything
            if self.c is None: self.chain.setAllPixels(Black.getPixelColor())
            self.chain.setChainBrightness(1.0)
            self.c = self.getNextPaletteEntry()
            self.chainPos=0 if self.direction else self.chainLen-1
            self.init = False

        # the main shifting is done here

        if self.multiColored:
            self.c = self.getNextPaletteEntry()

        if self.direction:
            self.chain.shiftRight(1, self.c.getPixelColor())
            self.chainPos+=1
            if self.chainPos == self.chainLen-1:
                self.init = True
        else:
            self.chain.shiftLeft(1, self.c.getPixelColor())
            self.chainPos-=1
            if self.chainPos == 0:
                self.init = True

        self.refreshCanvas()

class WipeRight(Wipe):
    def __init__(self,  **kwargs):
        super(WipeRight, self).__init__( **kwargs)
        self.direction = True

class WipeLeft(Wipe):
    def __init__(self, **kwargs):
        super(WipeLeft, self).__init__( **kwargs)
        self.direction = False

