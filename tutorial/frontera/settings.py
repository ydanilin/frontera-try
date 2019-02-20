# these two parameters are pointing Frontera that it will run locally

SPIDER_FEED_PARTITIONS = 1
SPIDER_LOG_PARTITIONS = 1

# BACKEND = 'frontera.contrib.backends.sqlalchemy.Distributed'
BACKEND = 'tutorial.frontera.backend.WlwBackend'
SQLALCHEMYBACKEND_ENGINE = 'sqlite:///wlwjob.db'
SQLALCHEMYBACKEND_DROP_ALL_TABLES = False
SQLALCHEMYBACKEND_CLEAR_CONTENT = False
SQLALCHEMYBACKEND_ENGINE_ECHO = False

SQLALCHEMYBACKEND_MODELS = {
    'MetadataModel': 'frontera.contrib.backends.sqlalchemy.models.MetadataModel',
    'StateModel': 'frontera.contrib.backends.sqlalchemy.models.StateModel',
    # 'QueueModel': 'frontera.contrib.backends.sqlalchemy.models.QueueModel',
    'QueueModel': 'tutorial.frontera.models.WlwQueueModel',
    'DomainMetadataModel': 'frontera.contrib.backends.sqlalchemy.models.DomainMetadataModel',
}

STRATEGY = 'tutorial.frontera.strategy.WlwStrategy'
# STRATEGY = 'frontera.strategy.depth.BreadthFirstCrawlingStrategy'

# MAX_REQUESTS = 3
LOGGING_CONFIG = 'logging.conf'
