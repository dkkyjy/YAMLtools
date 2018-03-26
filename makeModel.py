import sys
from DmpST import maptools
from YAMLtools import NewModel, LoadModel

def FindSource(catalog, skycrd0_C, srcReg, outfile):
    catalog = LoadModel(catalog)

    model = NewModel()
    for srcName in catalog.SrcList:
        skycrd_C = catalog.GetSrcDir(srcName)
        rad = maptools.Sep(skycrd_C, skycrd0_C)
        if rad < srcReg:
            print(rad)
            srcDict = catalog.GetSrcDict(srcName)
            if srcDict['type'] == 'PointSource':
                model.AddPointSource(srcName)
            if srcDict['type'] == 'DiffuseSource':
                spatialFile = srcDict['file']
                model.AddDiffuseSource(srcName, SpatialFile=spatialFile)
            model.AddSpectralDict(srcName, srcDict['spectrum'])
            model.AddSpatialDict(srcName, srcDict['spatialModel'])
            print(srcDict)
    model.SaveModel(outfile)


if __name__ == '__main__':
    skycrd0_C = (float(sys.argv[1]), float(sys.argv[2]))
    srcReg = float(sys.argv[3])
    catalog = 'PointSource.yaml'
    outfile = 'myModel.yaml'
    FindSource(catalog, skycrd0_C, srcReg, outfile)