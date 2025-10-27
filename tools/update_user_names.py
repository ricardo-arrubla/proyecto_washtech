import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.connection import db
from models.user import User

app = create_app()
with app.app_context():
    changed = False
    super_u = User.query.filter_by(email='super@washtech.com').first()
    if super_u:
        print('Antes super:', super_u.name)
        super_u.name = 'Ricardo'
        changed = True
        print('Actualizado super a:', super_u.name)
    else:
        print('Usuario super@washtech.com no encontrado')
    admin_u = User.query.filter_by(email='admin@washtech.com').first()
    if admin_u:
        print('Antes admin:', admin_u.name)
        admin_u.name = 'Camilo'
        changed = True
        print('Actualizado admin a:', admin_u.name)
    else:
        print('Usuario admin@washtech.com no encontrado')
    if changed:
        db.session.commit()
        print('Cambios guardados en la base de datos')
