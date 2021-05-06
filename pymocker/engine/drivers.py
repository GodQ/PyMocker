from pymocker.config import config


class EngineDriver:
    @classmethod
    def get_engine(cls, engine_type='process'):
        if not engine_type:
            engine_type = config.engine_type
        if engine_type == 'process':
            from pymocker.engine.process_engine import ProcessEngine
            return ProcessEngine
        else:
            raise Exception("No such engine")


# print(EngineDriver.get_engine())