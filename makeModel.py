import sys
from DmpST import maptools
from YAMLtools import NewModel, LoadModel
from astropy.coordinates import SkyCoord
from regions import PointSkyRegion, write_ds9


def FindCircleSource(catalog, skycrd0_C, srcRad, freeRad, outfile):
    catalog = LoadModel(catalog)

    model = NewModel()
    for srcName in catalog.SrcList:
        skycrd_C = catalog.GetSrcDir(srcName)
        rad = maptools.Sep(skycrd_C, skycrd0_C)
        if rad < srcRad:
            print(srcName, rad)
            srcDict = catalog.GetSrcDict(srcName)
            if srcDict['type'] == 'PointSource':
                model.AddPointSource(srcName)
            if srcDict['type'] == 'DiffuseSource':
                spatialFile = srcDict['spatialModel']['file']
                model.AddDiffuseSource(srcName, SpatialFile=spatialFile)
            model.AddSpectralDict(srcName, srcDict['spectrum'])
            model.AddSpatialDict(srcName, srcDict['spatialModel'])
    model.SaveModel(outfile)

    regionList = []
    model = LoadModel(outfile)
    for srcName in model.SrcList:
        skycrd_C = model.GetSrcDir(srcName)
        center = SkyCoord(*skycrd_C, unit='deg')
        region = PointSkyRegion(center)
        regionList.append(region)

        rad = maptools.Sep(skycrd_C, skycrd0_C)
        if rad > freeRad:
            for parName in model.FreeParDict[srcName]:
                print(parName)
                model.SetParFree(srcName, parName, 0)
    model.SaveModel(outfile)

    regfile = outfile.split('.')[0] + '.reg'
    write_ds9(regionList, regfile)


def FindBoxSource(catalog, GorC, srcReg, outfile):
    catalog = LoadModel(catalog)

    model = NewModel()
    for srcName in catalog.SrcList:
        skycrd_C = catalog.GetSrcDir(srcName)
        if GorC == 'C':
            xref, yref = skycrd_C
        if GorC == 'G':
            skycrd_G = maptools.skycrdC2G(skycrd_C)[0]
            xref, yref = skycrd_G
        if xref > xmin and xref < xmax and yref > ymin and yref < ymax:
            print(srcName, xref, yref)
            srcDict = catalog.GetSrcDict(srcName)
            if srcDict['type'] == 'PointSource':
                model.AddPointSource(srcName)
            if srcDict['type'] == 'DiffuseSource':
                spatialFile = srcDict['spatialModel']['file']
                model.AddDiffuseSource(srcName, SpatialFile=spatialFile)
            model.AddSpectralDict(srcName, srcDict['spectrum'])
            model.AddSpatialDict(srcName, srcDict['spatialModel'])
    model.SaveModel(outfile)

    regionList = []
    model = LoadModel(outfile)
    for srcName in model.SrcList:
        skycrd_C = model.GetSrcDir(srcName)
        center = SkyCoord(*skycrd_C, unit='deg')
        region = PointSkyRegion(center)
        regionList.append(region)

        if GorC == 'C':
            xref, yref = skycrd_C
        if GorC == 'G':
            skycrd_G = maptools.skycrdC2G(skycrd_C)[0]
            xref, yref = skycrd_G
        xmin, xmax, ymin, ymax = freeReg
        if xref < xmin or xref > xmax or yref < ymin or yref > ymax:
            for parName in model.FreeParDict[srcName]:
                print(parName)
                model.SetParFree(srcName, parName, 0)
    model.SaveModel(outfile)

    regfile = outfile.split('.')[0] + '.reg'
    write_ds9(regionList, regfile)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catalog', type=str, help='catalog file to use, xml')
    parser.add_argument('-o', '--outfile', type=str, default='myModel.xml', help='Name of output file')
    parser.add_argument('GorC', type=str, help='GAL(G) or CEL(C)')
    #parser.add_argument('xref', type=float, help='xref of circle source region')
    #parser.add_argument('yref', type=float, help='yref of circle source region')
    #parser.add_argument('srcRad', type=float, help='radii of circle source region')
    #parser.add_argument('freeRad', type=float, help='radii of circle free source region')
    parser.add_argument('xmin', type=float, help='xmin of box source region')
    parser.add_argument('xmax', type=float, help='xmax of box source region')
    parser.add_argument('ymin', type=float, help='ymin of box source region')
    parser.add_argument('ymax', type=float, help='ymax of box source region')
    parser.add_argument('freexmin', type=float, help='xmin of box free source region')
    parser.add_argument('freexmax', type=float, help='xmax of box free source region')
    parser.add_argument('freeymin', type=float, help='ymin of box free source region')
    parser.add_argument('freeymax', type=float, help='ymax of box free source region')

    args = parser.parse_args()
    '''
    parser.add_argument('-G', '--galfile', type=str, default='gll_iem_v06.fits', help='Name of Galactic diffuse model')
    parser.add_argument('-g', '--galname', type=str, default='gal_diffuse_model', help='Name of Galactic diffuse model in xml file')
    parser.add_argument('-I', '--isofile', type=str, default='iso_P8R2_SOURCE_V6_v06.txt', help='Name of Isotropic diffuse model')
    parser.add_argument('-i', '--isoname', type=str, default='iso_diffuse_model', help='Name of Isotropic model in xml file')
    '''

    '''
    coord = args.GorC
    if GorC == 'C':
        skycrd0_C = (args.xref, args.yref)
    if GorC == 'G':
        skycrd0_G = (args.xref, args.yref)
        skycrd0_C = maptools.skycrdG2C(skycrd0_G)
    FindSource(args.catalog, skycrd0_C, args.srcRad, args.freeRad, args.outfile)
    '''

    srcReg = (args.xmin, args.xmax, args.ymin, args.ymax)
    freeReg = (args.freexmin, args.freexmax, args.freeymin, args.freeymax)
    FindBoxSource(args.catalog, args.GorC, srcReg, freeReg, args.outfile)