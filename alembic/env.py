from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.database.base import Base

# সব models import করতে হবে
from app.models.user import User


config = context.config


# .env থেকে DATABASE_URL নিয়ে Alembic-এ set করছি
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata