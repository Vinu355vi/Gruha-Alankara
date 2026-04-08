import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import cv2

class DesignModel:
    def __init__(self):
        self.style_classifier = None
        self.color_extractor = None
        
    def analyze_room_image(self, image_path):
        """
        Analyze room image to extract features
        """
        # Load image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Extract features
        features = {
            'dimensions': self._estimate_dimensions(image),
            'colors': self._extract_colors(image),
            'furniture': self._detect_furniture(image),
            'lighting': self._analyze_lighting(image)
        }
        
        return features
    
    def _estimate_dimensions(self, image):
        """
        Estimate room dimensions from image
        """
        # In production, use depth estimation or reference objects
        height, width, _ = image.shape
        
        # Mock dimensions based on image aspect ratio
        aspect_ratio = width / height
        estimated_width = 5.0  # meters
        estimated_length = estimated_width / aspect_ratio
        estimated_height = 2.7  # standard ceiling height
        
        return {
            'width': estimated_width,
            'length': estimated_length,
            'height': estimated_height
        }
    
    def _extract_colors(self, image, n_colors=5):
        """
        Extract dominant colors from image using K-means clustering
        """
        # Resize image for faster processing
        image_resized = cv2.resize(image, (100, 100))
        pixels = image_resized.reshape(-1, 3)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42)
        kmeans.fit(pixels)
        
        # Get dominant colors
        colors = kmeans.cluster_centers_.astype(int)
        
        # Count pixels in each cluster
        labels = kmeans.labels_
        counts = np.bincount(labels)
        percentages = (counts / len(labels) * 100).round(1)
        
        # Format colors as hex
        color_list = []
        for i, color in enumerate(colors):
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            color_list.append({
                'rgb': color.tolist(),
                'hex': hex_color,
                'percentage': percentages[i]
            })
        
        return color_list
    
    def _detect_furniture(self, image):
        """
        Detect furniture in the image
        In production, use YOLO or similar object detection
        """
        # Mock furniture detection
        furniture_items = [
            {'type': 'sofa', 'confidence': 0.95, 'position': [2.5, 1.5]},
            {'type': 'coffee_table', 'confidence': 0.87, 'position': [2.5, 3.5]},
            {'type': 'tv_stand', 'confidence': 0.92, 'position': [4.5, 2.5]}
        ]
        
        return furniture_items
    
    def _analyze_lighting(self, image):
        """
        Analyze lighting conditions in the image
        """
        # Convert to HSV for better lighting analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Analyze brightness (V channel)
        brightness = np.mean(hsv[:, :, 2])
        
        # Analyze contrast
        contrast = np.std(hsv[:, :, 2])
        
        # Determine lighting conditions
        if brightness > 180:
            condition = 'bright'
        elif brightness > 100:
            condition = 'moderate'
        else:
            condition = 'dim'
        
        return {
            'brightness': float(brightness),
            'contrast': float(contrast),
            'condition': condition,
            'natural_light_estimate': min(brightness / 255 * 100, 100)
        }
    
    def generate_design_suggestions(self, room_features, preferences):
        """
        Generate design suggestions based on room analysis and user preferences
        """
        suggestions = {
            'color_palette': self._suggest_colors(room_features, preferences),
            'furniture_layout': self._suggest_layout(room_features, preferences),
            'lighting_recommendations': self._suggest_lighting(room_features),
            'style_matches': self._match_style(room_features, preferences)
        }
        
        return suggestions
    
    def _suggest_colors(self, room_features, preferences):
        """
        Suggest color palette based on room and preferences
        """
        current_colors = room_features['colors']
        preferred_style = preferences.get('style', 'modern')
        
        # Color harmony rules
        color_palettes = {
            'modern': ['#2C3E50', '#E74C3C', '#ECF0F1', '#3498DB', '#95A5A6'],
            'minimalist': ['#FFFFFF', '#F5F5F5', '#E0E0E0', '#BDBDBD', '#9E9E9E'],
            'scandinavian': ['#F9F9F9', '#E8E8E8', '#B8B8B8', '#88A9C9', '#C9B88A'],
            'industrial': ['#2C3E50', '#7F8C8D', '#BDC3C7', '#E67E22', '#D35400']
        }
        
        return color_palettes.get(preferred_style, color_palettes['modern'])
    
    def _suggest_layout(self, room_features, preferences):
        """
        Suggest furniture layout
        """
        dimensions = room_features['dimensions']
        room_type = preferences.get('room_type', 'living')
        
        # Predefined layouts for different room types
        layouts = {
            'living': [
                {'item': 'sofa', 'position': [2.5, 1.5], 'rotation': 0},
                {'item': 'coffee_table', 'position': [2.5, 3.5], 'rotation': 0},
                {'item': 'tv_stand', 'position': [4.5, 2.5], 'rotation': 180},
                {'item': 'bookshelf', 'position': [1.0, 4.0], 'rotation': 90}
            ],
            'bedroom': [
                {'item': 'bed', 'position': [3.0, 2.5], 'rotation': 0},
                {'item': 'nightstand_left', 'position': [2.0, 2.5], 'rotation': 0},
                {'item': 'nightstand_right', 'position': [4.0, 2.5], 'rotation': 0},
                {'item': 'dresser', 'position': [2.5, 4.5], 'rotation': 0}
            ]
        }
        
        return layouts.get(room_type, layouts['living'])
    
    def _suggest_lighting(self, room_features):
        """
        Suggest lighting improvements
        """
        lighting = room_features['lighting']
        suggestions = []
        
        if lighting['natural_light_estimate'] < 50:
            suggestions.append({
                'type': 'natural',
                'suggestion': 'Add mirrors to reflect natural light',
                'priority': 'high'
            })
        
        if lighting['brightness'] < 100:
            suggestions.append({
                'type': 'ambient',
                'suggestion': 'Add ambient lighting (ceiling lights)',
                'priority': 'medium'
            })
        
        suggestions.append({
            'type': 'accent',
            'suggestion': 'Add accent lighting to highlight features',
            'priority': 'low'
        })
        
        return suggestions
    
    def _match_style(self, room_features, preferences):
        """
        Match room with design styles
        """
        # Mock style matching
        styles = [
            {'name': 'Modern', 'match_percentage': 85},
            {'name': 'Minimalist', 'match_percentage': 72},
            {'name': 'Scandinavian', 'match_percentage': 68},
            {'name': 'Industrial', 'match_percentage': 45}
        ]
        
        return styles