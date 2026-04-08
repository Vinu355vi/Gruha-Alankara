from app import app, db, User, Design, SavedItem, UserPreference
from werkzeug.security import generate_password_hash
import json
from datetime import datetime
import random

def seed_database():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Check if user exists
        user = User.query.filter_by(username='demo_user').first()
        if not user:
            print("Creating demo user...")
            hashed_password = generate_password_hash('password123')
            user = User(
                username='demo_user',
                email='demo@example.com',
                password_hash=hashed_password
            )
            db.session.add(user)
            db.session.commit()
        
        print(f"Using user: {user.username}")

        # Add sample designs if none exist
        if not user.designs:
            print("Adding sample designs...")
            designs_data = [
                {
                    'room_type': 'Living Room',
                    'style': 'Modern',
                    'status': 'completed',
                    'image_path': '/static/images/designs/living-room-modern.jpg',
                    'ar_model_path': '/static/models/living-room.glb'
                },
                {
                    'room_type': 'Bedroom',
                    'style': 'Minimalist',
                    'status': 'in_progress',
                    'image_path': '/static/images/designs/bedroom-minimal.jpg',
                    'ar_model_path': None
                },
                {
                    'room_type': 'Kitchen',
                    'style': 'Industrial',
                    'status': 'completed',
                    'image_path': '/static/images/designs/kitchen-industrial.jpg',
                    'ar_model_path': '/static/models/kitchen.glb'
                },
                 {
                    'room_type': 'Office',
                    'style': 'Scandinavian',
                    'status': 'in_progress',
                    'image_path': '/static/images/designs/office-scandi.jpg',
                    'ar_model_path': None
                }
            ]

            for d_data in designs_data:
                design = Design(
                    user_id=user.id,
                    room_type=d_data['room_type'],
                    style=d_data['style'],
                    dimensions=json.dumps({'width': 5, 'length': 4, 'height': 3}),
                    elements=json.dumps([]),
                    image_path=d_data['image_path'],
                    ar_model_path=d_data['ar_model_path'],
                    status=d_data['status']
                )
                db.session.add(design)
        
        # Add saved items if none exist
        if not user.saved_items:
            print("Adding saved items...")
            items_data = [
                {'name': 'Velvet Sofa', 'type': 'furniture', 'price': 1200, 'image': '/static/images/shop/sofa.jpg'},
                {'name': 'Modern Lamp', 'type': 'decor', 'price': 150, 'image': '/static/images/shop/lamp.jpg'},
                {'name': 'Wooden Coffee Table', 'type': 'furniture', 'price': 350, 'image': '/static/images/shop/table.jpg'},
                {'name': 'Abstract Wall Art', 'type': 'decor', 'price': 80, 'image': '/static/images/shop/art.jpg'}
            ]

            for item in items_data:
                saved_item = SavedItem(
                    user_id=user.id,
                    item_id=f"item_{random.randint(1000, 9999)}",
                    item_type=item['type'],
                    name=item['name'],
                    image_url=item['image'],
                    price=item['price']
                )
                db.session.add(saved_item)

        # Add user preferences
        if not user.preferences:
             print("Adding user preferences...")
             pref = UserPreference(
                 user_id=user.id,
                 preferred_style='Modern',
                 color_preferences=json.dumps(['#FF5733', '#33FF57']),
                 budget_range='1000-5000',
                 room_types=json.dumps(['Living Room', 'Bedroom'])
             )
             db.session.add(pref)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
