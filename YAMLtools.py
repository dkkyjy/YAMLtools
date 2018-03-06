import yaml
from pprint import pprint
from collections import Counter

class YAMLmodel(object):
    def __init__(self, filename):
        self.filename = filename.split('.yaml')[0]
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

        self.NumDict = dict(Counter(self.SrcList))
        self.SrcList = list(self.NumDict.keys())
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
        outfile = self.filename + '_SetParScaledValue_{}_{}_{}.yaml'.format(srcName, parName, value)
        with open(outfile, 'w') as f:
            yaml.dump(self.modelDict, f)
        return self.__init__(outfile)

    def SetParScale(self, srcName, parName, scale):
        self.modelDict[srcName]['spectrum'][parName]['scale'] = str(scale)
        outfile = self.filename + '_SetParScale_{}_{}_{}.yaml'.format(srcName, parName, scale)
        with open(outfile, 'w') as f:
            yaml.dump(self.modelDict, f)
        return self.__init__(outfile)

    def SetParFree(self, srcName, parName, free):
        self.modelDict[srcName]['spectrum'][parName]['free'] = str(free)
        outfile = self.filename + '_SetParFree_{}_{}_{}.yaml'.format(srcName, parName, free)
        with open(outfile, 'w') as f:
            yaml.dump(self.modelDict, f)
        return self.__init__(outfile)


if __name__ == '__main__':
    modelfile = 'YAMLmodel.yaml'
    model = YAMLmodel(modelfile)

    pprint(model.SrcList)
    pprint(model.FixSrcList)
    pprint(model.FreeSrcList)
    pprint(model.ParList)
    pprint(model.FixParList)
    pprint(model.FreeParList)
    pprint(model.NumDict)
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
