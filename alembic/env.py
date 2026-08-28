from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.database.base import Base

from app.models.user import User


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


print("TABLES:", Base.metadata.tables.keys())

target_metadata = Base.metadata