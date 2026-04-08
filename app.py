from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    designs = db.relationship('Design', backref='user', lazy=True)
    saved_items = db.relationship('SavedItem', backref='user', lazy=True)
    preferences = db.relationship('UserPreference', backref='user', uselist=False)

class SavedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.String(50)) # ID from furniture library
    item_type = db.Column(db.String(50)) # e.g., 'furniture', 'decor'
    name = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    preferred_style = db.Column(db.String(50))
    color_preferences = db.Column(db.JSON)
    budget_range = db.Column(db.String(20))
    room_types = db.Column(db.JSON)

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_type = db.Column(db.String(50))
    style = db.Column(db.String(50))
    dimensions = db.Column(db.JSON)
    elements = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200)) # Maybe related to Saved Items?
    ar_model_path = db.Column(db.String(200)) # Maybe related to AR Previews?
    status = db.Column(db.String(20), default='in_progress') # 'in_progress', 'completed'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and check_password_hash(user.password_hash, data['password']):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        hashed_password = generate_password_hash(data['password'])
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    return render_template('login.html', show_register=True)

@app.route('/dashboard')
@login_required
def dashboard():
    designs = current_user.designs
    saved_items_count = len(current_user.saved_items)
    total_designs = len(designs)
    # Count designs with AR models or simply treat AR usage as a metric
    ar_previews_count = sum(1 for d in designs if d.ar_model_path)
    # Count designs that are in progress
    in_progress_count = sum(1 for d in designs if getattr(d, 'status', 'in_progress') == 'in_progress')
    
    # Sort designs by creation date, newest first
    designs.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('dashboard.html', 
                         user=current_user,
                         recent_projects=designs[:5], # Show top 5 recent designs
                         stats={
                             'total_designs': total_designs,
                             'saved_items': saved_items_count,
                             'ar_previews': ar_previews_count,
                             'in_progress': in_progress_count
                         })

@app.route('/ar-viewer')
@login_required
def ar_viewer():
    return render_template('ar-viewer.html')

@app.route('/design-recommendations')
@login_required
def design_recommendations():
    return render_template('design-recommendations.html')

@app.route('/room-analysis')
@login_required
def room_analysis():
    return render_template('room-analysis.html')


from utils.room_analyzer import RoomAnalyzer

from utils.room_analyzer import RoomAnalyzer

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initialize analyzer
room_analyzer = RoomAnalyzer()

# API Routes for AI/AR Features
@app.route('/api/analyze-room', methods=['POST'])
@login_required
def analyze_room():
    if 'room_image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['room_image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    relative_path = os.path.join('room_images', filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    
    # Use real RoomAnalyzer
    try:
        analysis_result = room_analyzer.analyze_image(filepath)
        
        # Transform result to match frontend expectations if necessary
        formatted_result = {
            'image_url': url_for('uploaded_file', filename=relative_path.replace('\\', '/')),
            'dimensions': analysis_result.get('dimensions', {}),
            'lighting_conditions': analysis_result.get('lighting', {}).get('quality', 'good'),
            'lighting_details': { # Add details for frontend bars
                 'natural': analysis_result.get('lighting', {}).get('natural_light_estimate', 50),
                 'artificial': 100 - analysis_result.get('lighting', {}).get('natural_light_estimate', 50)
            },
            'wall_colors': [c['hex'] for c in analysis_result.get('colors', [])[:2]], # Top 2 colors
            'furniture_detected': analysis_result.get('furniture', []),
            'recommended_styles': [rec.get('style', rec) if isinstance(rec, dict) else rec for rec in analysis_result.get('recommendations', [])],
            'color_palette_suggestions': analysis_result.get('colors', []), # For the dominant color list
            'recommended_palette': analysis_result.get('recommended_palette', []) # For the generated 3-color palette
        }
        
        return jsonify(formatted_result)
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/generate-design-image', methods=['POST'])
@login_required
def generate_design_image():
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        style = data.get('style', 'Modern')
        
        # Parse filename from URL
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
            
        # Extract relative path from URL (Assuming /uploads/room_images/...)
        filename = image_url.split('/uploads/')[-1]
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
             return jsonify({'error': 'Original image not found'}), 404

        # Generate new filename
        new_filename = f"generated_{uuid.uuid4()}.jpg"
        output_relative_path = os.path.join('generated', new_filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_relative_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Simulate AI Image Generation using PIL
        from PIL import Image, ImageEnhance, ImageOps
        import random
        
        img = Image.open(input_path)
        img = img.convert('RGB')
        
        # Apply style-based modifications
        if style == 'Minimalist':
            # Increase brightness, slightly desaturate
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.8)
        elif style == 'Modern':
            # Increase contrast, slightly cool tone
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            # Overlay blue tint
            overlay = Image.new('RGB', img.size, (0, 0, 50))
            img = Image.blend(img, overlay, 0.1)
        elif style == 'Scandinavian':
            # Warm tone, bright
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
            overlay = Image.new('RGB', img.size, (50, 40, 0)) # Warm
            img = Image.blend(img, overlay, 0.1)
        elif style == 'Industrial':
             # High contrast, grayscale-ish
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.5)

        img.save(output_path)
        
        return jsonify({
            'success': True,
            'generated_image_url': url_for('uploaded_file', filename=output_relative_path.replace('\\', '/'))
        })

    except Exception as e:
        print(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-recommendations', methods=['POST'])
@login_required
def generate_recommendations():
    data = request.get_json()
    
    room_type = data.get('room_type')
    style_preference = data.get('style_preference')
    dimensions = data.get('dimensions')
    budget = data.get('budget')
    
    # AI-powered recommendation generation
    recommendations = generate_design_recommendations(
        room_type, style_preference, dimensions, budget
    )
    
    return jsonify(recommendations)

@app.route('/api/save-design', methods=['POST'])
@login_required
def save_design():
    data = request.get_json()
    
    image_path = None # Default fallback, let template handle it
    
    if 'image_data' in data and data['image_data']:
        try:
            import base64
            image_data = data['image_data'].split(',')[1]
            image_binary = base64.b64decode(image_data)
            filename = f"design_{uuid.uuid4()}.png"
            filepath = os.path.join(app.root_path, 'static/images/designs', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(image_binary)
            image_path = filename
        except Exception as e:
            print(f"Error saving design image: {e}")
            
    design = Design(
        user_id=current_user.id,
        room_type=data['room_type'],
        style=data['style'],
        dimensions=data['dimensions'],
        elements=data['elements'],
        image_path=image_path,
        ar_model_path=data.get('ar_model_path')
    )
    
    db.session.add(design)
    db.session.commit()
    
    return jsonify({'success': True, 'design_id': design.id})

@app.route('/api/ar/place-furniture', methods=['POST'])
@login_required
def place_furniture_ar():
    data = request.get_json()
    
    furniture_model = data.get('furniture_model')
    position = data.get('position')
    rotation = data.get('rotation')
    scale = data.get('scale')
    
    # Generate AR placement data
    ar_data = generate_ar_placement(furniture_model, position, rotation, scale)
    
    return jsonify(ar_data)

# AI Helper Functions
def analyze_room_with_ai(image_path):
    """
    AI-powered room analysis function
    """
    # Simulated AI analysis - In production, integrate with actual ML models
    return {
        'dimensions': {
            'width': 5.2,
            'length': 4.8,
            'height': 2.7
        },
        'lighting_conditions': 'good',
        'wall_colors': ['#F5F5F5', '#E8E8E8'],
        'furniture_detected': [
            {'type': 'sofa', 'confidence': 0.95},
            {'type': 'table', 'confidence': 0.87},
            {'type': 'chair', 'confidence': 0.92}
        ],
        'recommended_styles': ['Modern', 'Minimalist', 'Contemporary'],
        'color_palette_suggestions': [
            {'primary': '#2C3E50', 'secondary': '#E74C3C', 'accent': '#ECF0F1'},
            {'primary': '#34495E', 'secondary': '#16A085', 'accent': '#BDC3C7'}
        ]
    }

def generate_design_recommendations(room_type, style, dimensions, budget):
    """
    AI-powered design recommendation generator
    """
    # Simulated recommendations - In production, use ML models
    recommendations = {
        'furniture_layout': [
            {'item': 'Sofa', 'position': [2.5, 0, 1.5], 'rotation': 0, 'model': 'modern_sofa_01'},
            {'item': 'Coffee Table', 'position': [2.5, 0, 3.5], 'rotation': 0, 'model': 'glass_table_01'},
            {'item': 'TV Unit', 'position': [4.5, 0, 2.5], 'rotation': 180, 'model': 'tv_stand_01'},
            {'item': 'Bookshelf', 'position': [1.0, 0, 4.0], 'rotation': 90, 'model': 'bookshelf_01'}
        ],
        'color_scheme': {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#e74c3c',
            'walls': '#ecf0f1'
        },
        'lighting_suggestions': [
            {'type': 'ambient', 'position': [2.5, 2.5, 2.5], 'intensity': 0.8},
            {'type': 'accent', 'position': [1.0, 1.8, 1.0], 'intensity': 0.5}
        ],
        'estimated_cost': {
            'furniture': 1500,
            'lighting': 300,
            'decor': 200,
            'total': 2000
        },
        'shopping_links': [
            {'item': 'Modern Sofa', 'price': 599, 'link': '#', 'store': 'IKEA'},
            {'item': 'Glass Coffee Table', 'price': 199, 'link': '#', 'store': 'Wayfair'}
        ]
    }
    
    return recommendations

def generate_ar_placement(model_name, position, rotation, scale):
    """
    Generate AR placement data for 3D models
    """
    return {
        'model_url': f'/static/models/{model_name}.glb',
        'position': position,
        'rotation': rotation,
        'scale': scale,
        'animation': 'idle',
        'interaction': True
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)