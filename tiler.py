import os
import re
import math
import subprocess
from wand.image import Image

class Tiler:
    '''Scale a tile map up and down in powers of 2.'''
    def __init__(self, filename='{x},{z}.png', path='.', zoomOut=4, zoomIn=1):
        self.path = path
        self.filename = filename
        self.pattern = re.compile('^' + self.filename
           .replace('{x}', '(-?[0-9]+)')
           .replace('{z}', '(-?[0-9]+)') + '$')
        self.zoomOut = zoomOut
        self.zoomIn = zoomIn

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
        return coords

    def scaleDown(self, src, target):
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
                    print('Tile {i},{j}: -'.format(i=i,j=j))
                    continue
            pics = [pic if os.path.isfile(pic) else 'null:' for pic in pics]
            print('Tile {i},{j}: Update'.format(i=i,j=j))
            subprocess.call(['montage', '-mode', 'concatenate', '-background', 'None', '-geometry', '256x256'] + pics + [t])

    def scaleUp(self, src, target):
        coords = self.findTiles(src)
        for x,z in coords:
            source = src + self.filename.format(x=x,z=z)
            with Image(filename=source) as img:
                for i,j in ((0,0),(1,0),(0,1),(1,1)):
                    dest = target + self.filename.format(x=2*x+i,z=2*z+j)
                    if os.path.isfile(dest):
                        if os.path.getmtime(source) <= os.path.getmtime(dest):
                            continue
                    with img[i*256:i*256+256, j*256:j*256+256] as tile:
                        tile.resize(512,512)
                        print("Getting {},{} from {},{} to {},{}".format(i,j,x,z,2*x+i,2*z+j))
                        tile.save(filename=dest)

Tiler(path='day', zoomOut=0).execute()
