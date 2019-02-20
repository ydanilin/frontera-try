from sqlalchemy import Column, String
from frontera.contrib.backends.sqlalchemy.models import QueueModel


class WlwQueueModel(QueueModel):

    category = Column(String(64))
