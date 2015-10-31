import os
import re
import math
import subprocess
import argparse
from wand.image import Image

class Tiler:
    '''Scale a tile map up and down in powers of 2.'''
    def __init__(self, filename='{x},{z}.png', path='.', zoomOut=4, zoomIn=1, verbose=False):
        self.path = path
        if not os.path.isdir(self.path + '/z0'):
            raise ValueError("The path {}/z0 does not exist.".format(self.path))
        self.filename = filename
        self.pattern = re.compile('^' + self.filename
           .replace('{x}', '(-?[0-9]+)')
           .replace('{z}', '(-?[0-9]+)') + '$')
        self.zoomOut = zoomOut
        self.zoomIn = zoomIn
        self.verbose = verbose

    def execute(self):
        for i in range(self.zoomOut):
            self.scaleDown(self.path + '/z{}/'.format(i), self.path + '/z{}/'.format(i+1))
        for i in range(0,-self.zoomIn,-1):
            self.scaleUp(self.path + '/z{}/'.format(i), self.path + '/z{}/'.format(i-1))

    def findTiles(self, path):
        coords = set()
        for f in os.listdir(path):
            match = self.pattern.match(f)
            if match:
                x, z = int(match.group(1)), int(match.group(2))
                coords.add((x,z))
        if not coords:
            raise ValueError("No files matching \"{}\" were found in {}/z0; check the filename pattern.".format(self.filename, self.path))
        return coords

    def scaleDown(self, src, target):
        ensurePath(target)
        coords = self.findTiles(src)
        tcoords = set()
        for i,j in coords:
            tcoords.add((math.floor(i/2), math.floor(j/2)))

        for k,l in tcoords:
            i,j = 2*k,2*l
            pics = [src + self.filename.format(x=x,z=z) for x,z in ((i,j),(i+1,j),(i,j+1),(i+1,j+1))]
            t = target + self.filename.format(x=k, z=l)
            if os.path.isfile(t):
                newest_tile = max([os.path.getmtime(pic) if os.path.isfile(pic) else 0 for pic in pics])
                if newest_tile <= os.path.getmtime(t):
                    self.log('Tile {i},{j}: -'.format(i=i,j=j))
                    continue
            pics = [pic if os.path.isfile(pic) else 'null:' for pic in pics]
            self.log('Tile {i},{j}: Update'.format(i=i,j=j))
            subprocess.call(['montage', '-mode', 'concatenate', '-background', 'None', '-geometry', '256x256'] + pics + [t])

    def scaleUp(self, src, target):
        ensurePath(target)
        coords = self.findTiles(src)
        for x,z in coords:
            source = src + self.filename.format(x=x,z=z)
            with Image(filename=source) as img:
                for i,j in ((0,0),(1,0),(0,1),(1,1)):
                    dest = target + self.filename.format(x=2*x+i,z=2*z+j)
                    if os.path.isfile(dest):
                        if os.path.getmtime(source) <= os.path.getmtime(dest):
                            self.log("Tile {},{}: Update".format(2*x+i,2*z+j))
                            continue
                    with img[i*256:i*256+256, j*256:j*256+256] as tile:
                        tile.resize(512,512)
                        self.log("Tile {},{}: Update".format(2*x+i,2*z+j))
                        tile.save(filename=dest)

    def log(self, text):
        if self.verbose:
            print(text)

def ensurePath(target):
    if not os.path.isdir(target):
        try:
            os.mkdir(target)
        except OSError:
            raise IOError("The path {} does not exist and could not be created.".format(target))

def parser():
    parser = argparse.ArgumentParser(
        prog='tiler',
        description='''Scale the image tiles up and down.
    '''
    )
    parser.add_argument(
        '-v', '--verbose', action='store_const',
        help='Print verbose messages', dest='verbose', const=True, default=False
    )
    parser.add_argument(
        '--path', type=str,
        help='Location of the z0 folder [=.]', dest='path', metavar='PATH', default='.'
    )
    parser.add_argument(
        '--filename', type=str,
        help='Pattern of the image filenames [={x},{z}.png]', metavar='FILENAME', dest='filename', default='{x},{z}.png'
    )
    parser.add_argument(
        '--up', type=int,
        help='How many zoom levels to scale up (each doubles the scale). [=1]', metavar='UP', dest='zoomIn', default='1'
    )
    parser.add_argument(
        '--down', type=int,
        help='How many zoom levels to scale down (each halves the scale). [=4]', metavar='DOWN', dest='zoomOut', default='4'
    )
    return parser

def main():
    args = parser().parse_args()
    try:
        Tiler(**vars(args)).execute()
    except Exception as e:
        print("Error:",e)
        if args.path == '.' and not os.path.isdir(args.path + '/z0'):
            parser().print_help()

main()
