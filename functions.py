from stable_baselines3 import PPO
import pygame
import numpy as np

		
# Functions for line of sight

def lineRectIntersectionPoints( line, rect, game_window ):
    """ Get the list of points where the line and rect
        intersect,  The result may be zero, one or two points.

        BUG: This function fails when the line and the side
                of the rectangle overlap """

    def linesAreParallel( x1,y1, x2,y2, x3,y3, x4,y4 ):
        """ Return True if the given lines (x1,y1)-(x2,y2) and
            (x3,y3)-(x4,y4) are parallel """
        return (((x1-x2)*(y3-y4)) - ((y1-y2)*(x3-x4)) == 0)

    def intersectionPoint( x1,y1, x2,y2, x3,y3, x4,y4 ):
        """ Return the point where the lines through (x1,y1)-(x2,y2)
            and (x3,y3)-(x4,y4) cross.  This may not be on-screen  """
        #Use determinant method, as per
        #Ref: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        Px = ((((x1*y2)-(y1*x2))*(x3 - x4)) - ((x1-x2)*((x3*y4)-(y3*x4)))) / (((x1-x2)*(y3-y4)) - ((y1-y2)*(x3-x4)))
        Py = ((((x1*y2)-(y1*x2))*(y3 - y4)) - ((y1-y2)*((x3*y4)-(y3*x4)))) / (((x1-x2)*(y3-y4)) - ((y1-y2)*(x3-x4)))
        return Px,Py

    ### Begin the intersection tests
    result = []
    line_x1, line_y1, line_x2, line_y2 = line   # split into components
    pos_x, pos_y, width, height = rect

    ### Convert the rectangle into 4 lines
    rect_lines = [ ( pos_x, pos_y, pos_x+width, pos_y ), ( pos_x, pos_y+height, pos_x+width, pos_y+height ),  # top & bottom
                    ( pos_x, pos_y, pos_x, pos_y+height ), ( pos_x+width, pos_y, pos_x+width, pos_y+height ) ] # left & right

    ### intersect each rect-side with the line
    for r in rect_lines:
        rx1,ry1,rx2,ry2 = r
        if ( not linesAreParallel( line_x1,line_y1, line_x2,line_y2, rx1,ry1, rx2,ry2 ) ):    # not parallel
            pX, pY = intersectionPoint( line_x1,line_y1, line_x2,line_y2, rx1,ry1, rx2,ry2 )  # so intersecting somewhere
            pX = round( pX )
            pY = round( pY )
            # Lines intersect, but is on the rectangle, and between the line end-points?
            if ( rect.collidepoint( pX, pY )   and
                    pX >= min( line_x1, line_x2 ) and pX <= max( line_x1, line_x2 ) and
                    pY >= min( line_y1, line_y2 ) and pY <= max( line_y1, line_y2 ) ):
                pygame.draw.circle( game_window, ( 200, 200, 200), ( pX, pY ), 4 )
                result.append( ( pX, pY ) )                                     # keep it
                if ( len( result ) == 2 ):
                    break   # Once we've found 2 intersection points, that's it
    return result

class Wall( pygame.sprite.Sprite):
    """ Rectangular objects that blocks line-of-sight, walls, obstacles """
    def __init__( self, x, y, width, height ):
        pygame.sprite.Sprite.__init__( self )
        self.image = pygame.Surface( ( width, height ) )
        self.rect  = self.image.get_rect();
        self.rect.topleft = ( x, y )
        self.image.fill( (0,0,255) )

    def getRect( self ):
        return self.rect


# Class Being for player/agent useful for collision and getting center.
# class Being( pygame.sprite.Sprite):
#     """  """
#     def __init__( self, x, y, colour=(255,255,0), size=48 ):
#         pygame.sprite.Sprite.__init__( self )
#         self.colour= colour
#         self.image = pygame.Surface( ( size, size ), pygame.SRCALPHA )
#         self.rect  = self.image.get_rect();
#         self.rect.center = ( x, y )
#         self.size  = size
#         self.seen  = False     

