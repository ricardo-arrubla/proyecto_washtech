"""
Script para poblar la base de datos con datos de prueba
Ejecutar: python seed_data.py
"""

from app import create_app
from database.connection import db
from models.user import User
from models.washing_machine import WashingMachine
from models.inventory import Inventory
from datetime import datetime, date

def seed_database():
    app = create_app()
    with app.app_context():
        print("🌱 Iniciando poblado de base de datos...")
        
        # Crear tablas si no existen
        db.create_all()
        print("✅ Tablas de base de datos creadas o verificadas")
        
        # Crear usuarios
        print("\n👤 Creando usuarios...")
        
        # SuperAdmin (nombre cambiado a Ricardo)
        if not User.query.filter_by(email='super@washtech.com').first():
            superadmin = User(
                name='Ricardo',
                email='super@washtech.com',
                phone='3001234567',
                address='Calle Principal 100, Tuluá',
                role='superadmin'
            )
            superadmin.set_password('super123')
            db.session.add(superadmin)
            print("✅ SuperAdmin (Ricardo) creado")
        
        # Admin (nombre cambiado a Camilo)
        if not User.query.filter_by(email='admin@washtech.com').first():
            admin = User(
                name='Camilo',
                email='admin@washtech.com',
                phone='3009876543',
                address='Avenida 5 #20-30, Tuluá',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin (Camilo) creado")
        
        # Operadores
        if not User.query.filter_by(email='operador@washtech.com').first():
            operador = User(
                name='Operador Principal',
                email='operador@washtech.com',
                phone='3008765432',
                address='Calle 12 #10-5, Tuluá',
                role='operador'
            )
            operador.set_password('operador123')
            db.session.add(operador)
            print("✅ Operador (Operador Principal) creado")
        
        # Clientes
        clientes_data = [
            {'name': 'María García', 'email': 'maria@email.com', 'phone': '3101234567', 'address': 'Carrera 10 #15-20'},
            {'name': 'Juan Pérez', 'email': 'juan@email.com', 'phone': '3207654321', 'address': 'Calle 8 #25-15'},
            {'name': 'Ana López', 'email': 'ana@email.com', 'phone': '3159876543', 'address': 'Avenida 3 #30-40'},
        ]
        
        for cliente_data in clientes_data:
            if not User.query.filter_by(email=cliente_data['email']).first():
                cliente = User(
                    name=cliente_data['name'],
                    email=cliente_data['email'],
                    phone=cliente_data['phone'],
                    address=cliente_data['address'],
                    role='cliente'
                )
                cliente.set_password('cliente123')
                db.session.add(cliente)
                print(f"✅ Cliente {cliente_data['name']} creado")
        
        db.session.commit()
        
        # Crear lavadoras
        print("\n🧺 Creando lavadoras...")
        
        lavadoras_data = [
            {
                'model': 'Samsung WF-15K',
                'capacity': '15 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora samsung 7.5kg.webp',
                'description': 'Lavadora de carga frontal con tecnología EcoBubble y tambor de diamante',
                'location': 'Bodega A - Zona 1',
                'date': date(2024, 1, 15)
            },
            {
                'model': 'LG TurboWash 360',
                'capacity': '20 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora LG 22 kg.webp',
                'description': 'Lavadora inteligente con AI DD y sistema TurboWash de alta eficiencia',
                'location': 'Bodega A - Zona 2',
                'date': date(2024, 2, 20)
            },
            {
                'model': 'Whirlpool Supreme Care',
                'capacity': '12 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora Roper.webp',
                'description': 'Lavadora con 6th Sense Technology y programa de vapor',
                'location': 'Bodega B - Zona 1',
                'date': date(2024, 3, 10)
            },
            {
                'model': 'Mabe Aqua Saver',
                'capacity': '10 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora analoga 22 kg.webp',
                'description': 'Lavadora con sistema de ahorro de agua y energía',
                'location': 'Bodega B - Zona 2',
                'date': date(2024, 3, 25)
            },
            {
                'model': 'Electrolux PerfectCare',
                'capacity': '18 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora Electrolux 16 kg.webp',
                'description': 'Lavadora industrial con múltiples programas de lavado',
                'location': 'Bodega C - Zona 1',
                'date': date(2024, 4, 5)
            },
            {
                'model': 'Haceb Clean Pro',
                'capacity': '14 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora Hceb 18 kg.webp',
                'description': 'Lavadora colombiana con sistema de lavado suave',
                'location': 'Bodega C - Zona 2',
                'date': date(2024, 4, 20)
            },
            {
                'model': 'Bosch Serie 8',
                'capacity': '16 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora Direct motion 18 kg.webp',
                'description': 'Lavadora alemana de alta gama con Home Connect',
                'location': 'Bodega A - Zona 3',
                'date': date(2024, 5, 1)
            },
            {
                'model': 'Samsung AddWash',
                'capacity': '13 kg',
                'status': 'mantenimiento',
                'image': '/static/images/lavadora Direct motion 18 kg.webp',
                'description': 'Lavadora con puerta adicional para agregar ropa durante el ciclo',
                'location': 'Taller de Mantenimiento',
                'date': date(2024, 5, 15)
            },
            {
                'model': 'LG Twin Wash',
                'capacity': '22 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora LG 22 kg.webp',
                'description': 'Sistema de doble lavadora para mayor productividad',
                'location': 'Bodega D - Zona 1',
                'date': date(2024, 6, 1)
            },
            {
                'model': 'General Electric Turbo',
                'capacity': '11 kg',
                'status': 'operativa',
                'image': '/static/images/lavadora analoga 22 kg.webp',
                'description': 'Lavadora con sistema turbo de alta velocidad',
                'location': 'Bodega D - Zona 2',
                'date': date(2024, 6, 15)
            }
        ]
        
        for lavadora_data in lavadoras_data:
            if not WashingMachine.query.filter_by(model=lavadora_data['model']).first():
                lavadora = WashingMachine(
                    model=lavadora_data['model'],
                    capacity=lavadora_data['capacity'],
                    operational_status=lavadora_data['status'],
                    acquisition_date=lavadora_data['date'],
                    image_url=lavadora_data['image'],
                    description=lavadora_data['description']
                )
                db.session.add(lavadora)
                db.session.flush()
                
                # Crear inventario
                inventario = Inventory(
                    washing_machine_id=lavadora.id,
                    availability=True if lavadora_data['status'] == 'operativa' else False,
                    location=lavadora_data['location']
                )
                db.session.add(inventario)
                print(f"✅ Lavadora {lavadora_data['model']} creada")
        
        db.session.commit()
        
        print("\n✨ ¡Base de datos poblada exitosamente!")
        print("\n📝 Credenciales de acceso:")
        print("=" * 50)
        print("SuperAdmin:")
        print("  Email: super@washtech.com")
        print("  Password: super123")
        print("\nAdmin:")
        print("  Email: admin@washtech.com")
        print("  Password: admin123")
        print("\nCliente de prueba:")
        print("  Email: maria@email.com")
        print("  Password: cliente123")
        print("=" * 50)

if __name__ == '__main__':
    seed_database()