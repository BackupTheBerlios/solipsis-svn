import os,sys

def main():
    from solipsis.util.parameter import Parameters
    
    configFileName = searchPath + '/conf/solipsis.conf'
    params = Parameters(configFileName)
    print params.getNetParams()
    params.setOption('navigator','scale', '2')
    
searchPath = os.path.dirname(os.path.dirname(sys.path[0]))

if __name__ == '__main__':
    sys.path.append(searchPath)
    main()
