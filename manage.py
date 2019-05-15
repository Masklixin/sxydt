

from flask_script import Manager

from flask_migrate import Migrate,MigrateCommand
from shizhang import app
from exts import db
from models import User,Question,Answer



manager=Manager(app)
#使用migrate绑定app,db
migrate=Migrate(app,db)
#迁移脚本的命令
manager.add_command('db',MigrateCommand)

if __name__=='__main__':
    manager.run()