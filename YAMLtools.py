import yaml
from pprint import pprint
from collections import Counter

class NewModel(object):
    def SaveModel(self, outfile):
        with open(outfile, 'w') as f:
            yaml.dump(self.modelDict, f)
    
    def __init__(self, filename):
        self.filename = filename
        self.modelDict = {}

    def AddPointSource(self, srcName, SpectralType, SpectralPars, skycrd_C):
        ra = str(skycrd_C[0])
        dec = str(skycrd_C[1])
        spectrum = {'type':SpectralType}
        for parName, parDict in SpectralPars.items():
            free = str(parDict['free'])
            scale = str(parDict['scale'])
            value = str(parDict['value'])
            parmin = str(parDict['min'])
            parmax = str(parDict['max'])
            spectrum[parName] = {'free':free, 'name':parName, 'max':parmax, 'min':parmin, 'scale':scale, 'value':value}

        source = {'name': srcName,
                  'type': 'PointSource',
                  'spectrum': spectrum,
                  'spatialModel': {'type': 'SkyDirFunction',
                                     'RA': {'free':'0', 'max':'360.', 'min':'-360.', 'scale':'1', 'value':ra},
                                    'DEC': {'free':'0', 'max':'90.', 'min':'-90.', 'scale':'1', 'value':dec}
                                  }
                 }
        self.modelDict[srcName] = source
        self.SaveModel(self.filename)

    def AddDiffuseSource(self, srcName, SpectralType, SpectralPars, SpatialType, SpatialFile, SpatialPar):
        spectrum = {'type':SpectralType}
        for parName, parDict in SpectralPars.items():
            free = str(parDict['free'])
            scale = str(parDict['scale'])
            value = str(parDict['value'])
            parmin = str(parDict['min'])
            parmax = str(parDict['max'])
            spectrum[parName] = {'free':free, 'name':parName, 'max':parmax, 'min':parmin, 'scale':scale, 'value':value}

        name = SpatialPar['name']
        free = str(SpatialPar['free'])
        scale = str(SpatialPar['scale'])
        value = str(SpatialPar['value'])
        parmin = str(SpatialPar['min'])
        parmax = str(SpatialPar['max'])
        spatialModel = {'type': SpatialType, 'file': SpatialFile}
        spatialModel[name] = {'free':free, 'name':name, 'min':parmin, 'max':parmax, 'scale':scale, 'value':value}

        source = {'name': srcName,
                  'type': 'DiffuseSource',
                  'spectrum': spectrum,
                  'spatialModel': spatialModel}
        self.modelDict[srcName] = source
        self.SaveModel(self.filename)


class LoadModel(NewModel):
    def __init__(self, filename):
        self.basename = filename.split('.yaml')[0]
        self.filename = filename
        with open(filename, 'r') as f:
            self.modelDict = yaml.load(f)

        self.SrcList = []
        self.FixSrcList = []
        self.FreeSrcList = []

        self.ParList = []
        self.FixParList = []
        self.FreeParList = []

        for source in self.modelDict.values():
            srcName = source['name']
            srcType = source['type']
            self.FixSrcList.append(srcName)

            spectrum = source['spectrum']
            SpectralType = spectrum['type']
            spatialModel = source['spatialModel']
            SpatialType = spatialModel['type']

            for parName, parameter in spectrum.items():
                self.SrcList.append(srcName)
                if 'free' not in parameter:
                    continue
                self.ParList.append(srcName + '__' + parName)
                if parameter['free'] == 0 or parameter['free'] == '0':
                    self.FixParList.append(srcName + '__' + parName)
                if parameter['free'] == 1 or parameter['free'] == '1':
                    self.FreeParList.append(srcName + '__' + parName)
                    self.FreeSrcList.append(srcName)
                    try:
                        self.FixSrcList.remove(srcName)
                    except:
                        pass

        self.ParsNumDict = dict(Counter(self.SrcList))
        self.SrcList = list(self.ParsNumDict.keys())
        self.FreeNumDict = dict(Counter(self.FreeSrcList))
        self.FreeSrcList = list(self.FreeNumDict.keys())

    def GetSrcInfo(self, srcName):
        source = self.modelDict[srcName]
        print(source.values())

    def GetSpectralType(self, srcName):
        spectrum = self.modelDict[srcName]['spectrum']
        print(spectrum.values())

    def GetSpatialType(self, srcName):
        spatialModel = self.modelDict[srcName]['spatialModel']
        print(spatialModel.values())

    def GetParInfo(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        print(parameter.values())

    def GetParFree(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        return parameter['free']

    def GetParScale(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        scale = float(parameter['scale'])
        return scale

    def GetParValue(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        value = float(parameter['value']) * float(parameter['scale'])
        try:
            error = float(parameter['error']) * float(parameter['scale'])
        except:
            error = None
        return value, error

    def GetParScaledValue(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        return parameter['value']

    def SetParScaledValue(self, srcName, parName, value):
        self.modelDict[srcName]['spectrum'][parName]['value'] = str(value)
        outfile = self.basename + '_SetParScaledValue_{}_{}_{}.yaml'.format(srcName, parName, value)
        self.SaveModel(outfile)

    def SetParScale(self, srcName, parName, scale):
        self.modelDict[srcName]['spectrum'][parName]['scale'] = str(scale)
        outfile = self.basename + '_SetParScale_{}_{}_{}.yaml'.format(srcName, parName, scale)
        self.SaveModel(outfile)

    def SetParFree(self, srcName, parName, free):
        self.modelDict[srcName]['spectrum'][parName]['free'] = str(free)
        outfile = self.basename + '_SetParFree_{}_{}_{}.yaml'.format(srcName, parName, free)
        self.SaveModel(outfile)

    def DelSource(self, srcName):
        del self.modelDict[srcName]
        outfile = self.basename + '_DelSource_{}.yaml'.format(srcName)
        self.SaveModel(outfile)


if __name__ == '__main__':
    filename = 'myYAMLmodel.yaml'
    myModel = NewModel(filename)

    SpectralType = 'PowerLaw'
    SpectralPars = {'Prefactor': {'free':1, 'max':1000, 'min':0.001, 'scale':1e-9, 'value':1},
                        'Index': {'free':1, 'max':5, 'min':1, 'scale':-1, 'value':2},
                        'Scale': {'free':0, 'max':2000, 'min':30, 'scale':1, 'value':100}}
    skycrd_C = (83.45, 21.72)
    myModel.AddPointSource('myPowerLaw_source', SpectralType, SpectralPars, skycrd_C)

    SpatialType = 'SpatialMap'
    SpatialFile = 'SpatialMap_source.fits'
    SpatialPar = {'name': "Normalization", 'free':1, 'min':0.001, 'max':1000, 'scale':1, 'value':100}
    myModel.AddDiffuseSource('myDiffuse_source', SpectralType, SpectralPars, SpatialType, SpatialFile, SpatialPar)

    filename = 'YAMLmodel.yaml'
    model = LoadModel(filename)
    model.AddPointSource('myPowerLaw_source', SpectralType, SpectralPars, skycrd_C)

    pprint(model.SrcList)
    pprint(model.FixSrcList)
    pprint(model.FreeSrcList)
    pprint(model.ParList)
    pprint(model.FixParList)
    pprint(model.FreeParList)
    pprint(model.ParsNumDict)
    pprint(model.FreeNumDict)

    srcName = 'PowerLaw_source'
    model.GetSrcInfo(srcName)
    model.GetSpectralType(srcName)
    model.GetSpatialType(srcName)

    parName = 'Prefactor'
    model.GetParInfo(srcName, parName)
    print(model.GetParFree(srcName, parName))
    print(model.GetParScale(srcName, parName))
    print(model.GetParValue(srcName, parName))
    print(model.GetParScaledValue(srcName, parName))

    model.SetParScaledValue(srcName, parName, 1)
    model.SetParScale(srcName, parName, 1e-10)
    model.SetParFree(srcName, parName, 0)

    model.DelSource('myPowerLaw_source')