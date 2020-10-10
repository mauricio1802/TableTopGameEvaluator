
    
def Inmutator(aClass):
    class Inmutable:
        def __init__(self, *args, **kargs ):
            self.__dict__['wrapped'] = aClass(*args, **kargs)
            
        def __getattr__(self, attr):
            return getattr(self.__dict__['wrapped'], attr)
        
        def __setattr__(self, attr, value):
            raise SetAttributeError("Can not change attributes of an inmutable class")
        
                
        
    return Inmutable



