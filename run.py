from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import create_app
import os
from app.models.models import User, Server, Service, ServerVersionRelationship, Version, Project

app, db = create_app("baseConfig")

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    print(app.url_map)
    print(app.root_path)
    # print(app.instance_path)

    manager.run()
