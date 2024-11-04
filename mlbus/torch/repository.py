from mlregistry import Registry

class Models:
    registry = Registry()

    @classmethod
    def register(cls, type: type):
        cls.registry.register('models', type)
        

class Optimizers:
    registry = Registry(excluded_positions=[0], exclude_parameters={'params'})
    
    @classmethod
    def register(cls, type: type):
        cls.registry.register('optimizers', type)


class Criterions:
    registry = Registry()
    
    @classmethod
    def register(cls, type: type):
        cls.registry.register('criterions', type)


class Datasets:
    registry = Registry(exclude_parameters={'root', 'download'})
    
    @classmethod
    def register(cls, type: type):
        cls.registry.register('datasets', type)


class Repository:
    models = Models()
    criterions = Criterions()
    optimizers = Optimizers()
    datasets = Datasets()

    