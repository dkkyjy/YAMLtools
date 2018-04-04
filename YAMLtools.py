import yaml
from pprint import pprint
from collections import Counter


class Model(object):
    def GetModelInfo(self, modelDict):
        self.SrcList = []
        self.FixSrcList = []
        self.FreeSrcList = []

        self.ParList = []
        self.FixParList = []
        self.FreeParList = []

        self.ParDict = {}
        self.FixParDict = {}
        self.FreeParDict = {}

        for source in modelDict.values():
            srcName = source['name']
            self.SrcList.append(srcName)
            spectrum = source['spectrum']
            try:
                SpectralType = spectrum.pop('type')
                SpectralFile = spectrum.pop('file')
            except KeyError:
                pass

            ParList = []
            FixParList = []
            FreeParList = []
            for parName, parameter in spectrum.items():
                ParList.append(parName)
                self.ParList.append(srcName + '__' + parName)
                if parameter['free'] == 0 or parameter['free'] == '0':
                    FixParList.append(parName)
                    self.FixParList.append(srcName + '__' + parName)
                if parameter['free'] == 1 or parameter['free'] == '1':
                    FreeParList.append(parName)
                    self.FreeParList.append(srcName + '__' + parName)
            self.ParDict[srcName] = ParList
            self.FixParDict[srcName] = FixParList
            self.FreeParDict[srcName] = FreeParList
            if FreeParList:
                self.FreeSrcList.append(srcName)
            else:
                self.FixSrcList.append(srcName)

        self.SrcNum = len(self.SrcList)
        self.FixSrcNum = len(self.FixSrcList)
        self.FreeSrcNum = len(self.FreeSrcList)

        self.ParNum = len(self.ParList)
        self.FixParNum = len(self.FixParList)
        self.FreeParNum = len(self.FreeParList)


class NewModel(Model):
    def __init__(self):
        self.modelDict = {}

    def AddSrcDict(self, srcName, srcDict):
        self.modelDict[srcName] = srcDict
        self.GetModelInfo(self.modelDict)

    def AddSpectralDict(self, srcName, spectialDict):
        self.modelDict[srcName]['spectrum'] = spectialDict
        self.GetModelInfo(self.modelDict)

    def AddSpatialDict(self, srcName, spatialDict):
        self.modelDict[srcName]['spatialModel'] = spatialDict
        self.GetModelInfo(self.modelDict)

    def AddPointSource(self, srcName, SpectralType=None, SpectralPars=None, skycrd_C=None):
        if SpectralType:
            spectrum = {'type':SpectralType}
        else:
            spectrum = {}
        if SpectralPars:
            for parName, parDict in SpectralPars.items():
                free = str(parDict['free'])
                scale = str(parDict['scale'])
                value = str(parDict['value'])
                parmin = str(parDict['min'])
                parmax = str(parDict['max'])
                spectrum[parName] = {'free':free, 'name':parName, 'max':parmax, 'min':parmin, 'scale':scale, 'value':value}

        if skycrd_C:
            ra = str(skycrd_C[0])
            dec = str(skycrd_C[1])
            spatialModel = {'type': 'SkyDirFunction',
                                 'RA': {'free':'0', 'max':'360.', 'min':'-360.', 'scale':'1', 'value':ra},
                                'DEC': {'free':'0', 'max':'90.', 'min':'-90.', 'scale':'1', 'value':dec}
                           }
        else:
            spatialModel = {}

        source = {'name': srcName,
                  'type': 'PointSource',
              'spectrum': spectrum,
          'spatialModel': spatialModel
                 }
        self.modelDict[srcName] = source
        self.GetModelInfo(self.modelDict)

    def AddDiffuseSource(self, srcName, SpectralType=None, SpectralPars=None, SpatialType=None, SpatialFile=None, SpatialPar=None):
        if SpectralType:
            spectrum = {'type':SpectralType}
        else:
            spectrum = {}
        if SpectralPars:
            for parName, parDict in SpectralPars.items():
                free = str(parDict['free'])
                scale = str(parDict['scale'])
                value = str(parDict['value'])
                parmin = str(parDict['min'])
                parmax = str(parDict['max'])
                spectrum[parName] = {'free':free, 'name':parName, 'max':parmax, 'min':parmin, 'scale':scale, 'value':value}

        if SpatialFile and SpatialType:
            spatialModel = {'type': SpatialType, 'file': SpatialFile}
        else:
            spatialModel = {}
        if SpatialPar:
            name = SpatialPar['name']
            free = str(SpatialPar['free'])
            scale = str(SpatialPar['scale'])
            value = str(SpatialPar['value'])
            parmin = str(SpatialPar['min'])
            parmax = str(SpatialPar['max'])
            spatialModel[name] = {'free':free, 'name':name, 'min':parmin, 'max':parmax, 'scale':scale, 'value':value}

        source = {'name': srcName,
                  'type': 'DiffuseSource',
                  'spectrum': spectrum,
                  'spatialModel': spatialModel}
        self.modelDict[srcName] = source
        self.GetModelInfo(self.modelDict)

    def SaveModel(self, outfile):
        with open(outfile, 'w') as f:
            yaml.dump(self.modelDict, f)
    

class LoadModel(NewModel):
    def __init__(self, filename):
        self.basename = filename.split('.yaml')[0]
        self.filename = filename
        with open(filename, 'r') as f:
            self.modelDict = yaml.load(f)
        self.GetModelInfo(self.modelDict)

    def GetSrcInfo(self, srcName):
        source = self.modelDict[srcName]
        print(source.values())

    def GetSrcDict(self, srcName):
        source = self.modelDict[srcName]
        return source

    def GetSrcDir(self, srcName):
        source = self.modelDict[srcName]
        if source['type'] == 'PointSource':
            ra = float(source['spatialModel']['RA']['value'])
            dec = float(source['spatialModel']['DEC']['value'])
        if source['type'] == 'DiffuseSource':
            ra = float(source['RA'])
            dec = float(source['DEC'])
        return (ra, dec)

    def GetSpectralInfo(self, srcName):
        spectrum = self.modelDict[srcName]['spectrum']
        print(spectrum.values())

    def GetSpectralDict(self, srcName):
        spectrum = self.modelDict[srcName]['spectrum']
        return spectrum

    def GetSpatialInfo(self, srcName):
        spatialModel = self.modelDict[srcName]['spatialModel']
        print(spatialModel.values())

    def GetSpatialDict(self, srcName):
        spatialModel = self.modelDict[srcName]['spatialModel']
        return spatialModel

    def GetParInfo(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        print(parameter.values())

    def GetParDict(self, srcName, parName):
        parameter = self.modelDict[srcName]['spectrum'][parName]
        return parameter

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
        self.GetModelInfo(self.modelDict)

    def SetParScale(self, srcName, parName, scale):
        self.modelDict[srcName]['spectrum'][parName]['scale'] = str(scale)
        self.GetModelInfo(self.modelDict)

    def SetParFree(self, srcName, parName, free):
        self.modelDict[srcName]['spectrum'][parName]['free'] = str(free)
        self.GetModelInfo(self.modelDict)

    def DelSource(self, srcName):
        del self.modelDict[srcName]
        self.GetModelInfo(self.modelDict)


if __name__ == '__main__':
    '''
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
    '''

    filename = 'YAMLmodel.yaml'
    model = LoadModel(filename)
    #model.AddPointSource('myPowerLaw_source', SpectralType, SpectralPars, skycrd_C)

    pprint(model.SrcList)
    pprint(model.FixSrcList)
    pprint(model.FreeSrcList)
    print(model.SrcNum, model.FixSrcNum, model.FreeSrcNum)
    pprint(model.ParList)
    pprint(model.FixParList)
    pprint(model.FreeParList)
    print(model.ParNum, model.FixParNum, model.FreeParNum)
    pprint(model.ParDict)
    pprint(model.FixParDict)
    pprint(model.FreeParDict)

    srcName = 'PowerLaw_source'
    model.GetSrcInfo(srcName)
    model.GetSpectralInfo(srcName)
    model.GetSpatialInfo(srcName)

    parName = 'Prefactor'
    model.GetParInfo(srcName, parName)
    print(model.GetParFree(srcName, parName))
    print(model.GetParScale(srcName, parName))
    print(model.GetParValue(srcName, parName))
    print(model.GetParScaledValue(srcName, parName))

    model.SetParScaledValue(srcName, parName, 1)
    model.SetParScale(srcName, parName, 1e-10)
    model.SetParFree(srcName, parName, 0)

    #model.DelSource('myPowerLaw_source')