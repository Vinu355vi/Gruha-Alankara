import numpy as np
from sklearn.ensemble import RandomForestRegressor
import json

class AIRecommendations:
    def __init__(self):
        self.style_model = None
        self.color_model = None
        self.furniture_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """
        Initialize AI models for recommendations
        """
        # Style recommendation model
        self.style_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Color harmony model
        self.color_model = RandomForestRegressor(n_estimators=50, random_state=42)
        
        # Furniture placement model
        self.furniture_model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    def get_style_recommendations(self, room_features, user_preferences):
        """
        Recommend interior design styles based on room and preferences
        """
        styles = [
            {'name': 'Modern', 'description': 'Clean lines, minimal ornamentation, functional'},
            {'name': 'Minimalist', 'description': 'Less is more, neutral colors, simple forms'},
            {'name': 'Scandinavian', 'description': 'Light wood, cozy textures, simple elegance'},
            {'name': 'Industrial', 'description': 'Raw materials, exposed elements, urban feel'},
            {'name': 'Bohemian', 'description': 'Rich patterns, eclectic mix, plants and textures'},
            {'name': 'Traditional', 'description': 'Classic details, rich colors, elegant furniture'},
            {'name': 'Contemporary', 'description': 'Current trends, curved lines, bold colors'},
            {'name': 'Mid-Century', 'description': 'Retro feel, organic shapes, tapered legs'}
        ]
        
        # Calculate style scores based on room features
        style_scores = []
        for style in styles:
            score = self._calculate_style_score(style, room_features, user_preferences)
            style_scores.append({
                **style,
                'match_score': score,
                'recommendations': self._get_style_specific_recommendations(style['name'])
            })
        
        # Sort by score
        style_scores.sort(key=lambda x: x['match_score'], reverse=True)
        
        return style_scores
    
    def _calculate_style_score(self, style, room_features, user_preferences):
        """
        Calculate how well a style matches the room and preferences
        """
        score = 50  # Base score
        
        # Adjust based on room lighting
        if room_features['lighting']['natural_light_estimate'] > 70:
            if style['name'] in ['Scandinavian', 'Modern']:
                score += 15
        elif room_features['lighting']['natural_light_estimate'] < 30:
            if style['name'] in ['Industrial', 'Bohemian']:
                score += 15
        
        # Adjust based on room size
        area = room_features['dimensions']['width'] * room_features['dimensions']['length']
        if area < 20:  # Small room
            if style['name'] in ['Minimalist', 'Modern']:
                score += 20
        elif area > 40:  # Large room
            if style['name'] in ['Traditional', 'Contemporary']:
                score += 20
        
        # Adjust based on user preferences
        if user_preferences.get('preferred_style') == style['name']:
            score += 30
        
        return min(100, max(0, score))
    
    def _get_style_specific_recommendations(self, style_name):
        """
        Get specific recommendations for a style
        """
        recommendations = {
            'Modern': [
                'Use clean lines and geometric shapes',
                'Incorporate metal and glass materials',
                'Choose neutral colors with bold accents'
            ],
            'Minimalist': [
                'Keep furniture to a minimum',
                'Use hidden storage solutions',
                'Stick to a monochromatic color scheme'
            ],
            'Scandinavian': [
                'Add light wood furniture',
                'Incorporate cozy textiles',
                'Maximize natural light'
            ],
            'Industrial': [
                'Expose brick or concrete walls',
                'Use metal piping and fixtures',
                'Add vintage or reclaimed pieces'
            ]
        }
        
        return recommendations.get(style_name, [])
    
    def generate_color_palette(self, base_color, style, room_type):
        """
        Generate harmonious color palette
        """
        # Color harmony algorithms
        palettes = {
            'monochromatic': self._generate_monochromatic(base_color),
            'complementary': self._generate_complementary(base_color),
            'analogous': self._generate_analogous(base_color),
            'triadic': self._generate_triadic(base_color)
        }
        
        # Choose palette based on style
        style_palette_map = {
            'Modern': 'complementary',
            'Minimalist': 'monochromatic',
            'Scandinavian': 'analogous',
            'Bohemian': 'triadic'
        }
        
        palette_type = style_palette_map.get(style, 'complementary')
        palette = palettes[palette_type]
        
        return {
            'type': palette_type,
            'colors': palette,
            'suggestions': self._get_color_suggestions(palette, room_type)
        }
    
    def _generate_monochromatic(self, base_color):
        """Generate monochromatic color scheme"""
        # Convert hex to RGB
        r, g, b = self._hex_to_rgb(base_color)
        
        colors = []
        for i in range(5):
            factor = 0.5 + i * 0.125  # 0.5 to 1.0
            new_r = int(min(255, r * factor))
            new_g = int(min(255, g * factor))
            new_b = int(min(255, b * factor))
            colors.append(self._rgb_to_hex([new_r, new_g, new_b]))
        
        return colors
    
    def _generate_complementary(self, base_color):
        """Generate complementary color scheme"""
        r, g, b = self._hex_to_rgb(base_color)
        
        # Complementary color
        comp_r = 255 - r
        comp_g = 255 - g
        comp_b = 255 - b
        
        return [
            base_color,
            self._rgb_to_hex([comp_r, comp_g, comp_b]),
            self._adjust_brightness(base_color, 0.7),
            self._adjust_brightness(base_color, 0.5),
            self._adjust_brightness(self._rgb_to_hex([comp_r, comp_g, comp_b]), 0.7)
        ]
    
    def _generate_analogous(self, base_color):
        """Generate analogous color scheme"""
        # Simplified - in production, use proper color theory
        return [
            base_color,
            self._adjust_hue(base_color, 30),
            self._adjust_hue(base_color, -30),
            self._adjust_brightness(base_color, 0.8),
            self._adjust_brightness(base_color, 0.6)
        ]
    
    def _generate_triadic(self, base_color):
        """Generate triadic color scheme"""
        return [
            base_color,
            self._adjust_hue(base_color, 120),
            self._adjust_hue(base_color, 240),
            self._adjust_brightness(base_color, 0.8),
            self._adjust_brightness(self._adjust_hue(base_color, 120), 0.8)
        ]
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb):
        """Convert RGB to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def _adjust_brightness(self, hex_color, factor):
        """Adjust color brightness"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = int(min(255, r * factor))
        g = int(min(255, g * factor))
        b = int(min(255, b * factor))
        return self._rgb_to_hex([r, g, b])
    
    def _adjust_hue(self, hex_color, angle):
        """Adjust color hue (simplified)"""
        # In production, use proper HSV conversion
        return hex_color  # Placeholder
    
    def _get_color_suggestions(self, palette, room_type):
        """Get color usage suggestions for each room type"""
        suggestions = {
            'living': 'Use the primary color for walls, secondary for furniture, and accent for decor',
            'bedroom': 'Use calming colors for walls, warm tones for bedding',
            'kitchen': 'Use lighter colors for cabinets, accent colors for backsplash',
            'bathroom': 'Use neutral colors for tiles, accent colors for accessories'
        }
        
        return suggestions.get(room_type, suggestions['living'])
    
    def recommend_furniture_placement(self, room_dimensions, furniture_items):
        """
        Recommend optimal furniture placement
        """
        width, length, height = room_dimensions
        
        # Calculate zones
        zones = self._calculate_zones(width, length)
        
        # Place furniture in appropriate zones
        placement = []
        for item in furniture_items:
            zone = self._find_best_zone(item, zones)
            if zone:
                position = self._calculate_position_in_zone(zone, item)
                placement.append({
                    'item': item['name'],
                    'zone': zone['name'],
                    'position': position,
                    'rotation': self._suggest_rotation(item, zone)
                })
        
        return placement
    
    def _calculate_zones(self, width, length):
        """Calculate functional zones in the room"""
        zones = [
            {'name': 'entertainment', 'x': width * 0.6, 'y': 0, 'z': length * 0.3, 'width': width * 0.3, 'length': length * 0.3},
            {'name': 'relaxation', 'x': width * 0.1, 'y': 0, 'z': length * 0.3, 'width': width * 0.3, 'length': length * 0.3},
            {'name': 'dining', 'x': width * 0.35, 'y': 0, 'z': length * 0.6, 'width': width * 0.3, 'length': length * 0.3}
        ]
        return zones
    
    def _find_best_zone(self, item, zones):
        """Find the best zone for an item"""
        # Map item types to zones
        zone_map = {
            'sofa': 'relaxation',
            'tv': 'entertainment',
            'table': 'dining',
            'bed': 'relaxation',
            'chair': 'relaxation'
        }
        
        zone_name = zone_map.get(item['type'].lower(), 'relaxation')
        for zone in zones:
            if zone['name'] == zone_name:
                return zone
        return zones[0]
    
    def _calculate_position_in_zone(self, zone, item):
        """Calculate optimal position within a zone"""
        import random
        
        # Add some randomness to avoid identical placements
        offset_x = random.uniform(-0.5, 0.5)
        offset_z = random.uniform(-0.5, 0.5)
        
        return [
            zone['x'] + offset_x,
            0,
            zone['z'] + offset_z
        ]
    
    def _suggest_rotation(self, item, zone):
        """Suggest rotation for an item"""
        # Default rotation (facing the room)
        return [0, 0, 0]
    
    def calculate_budget_optimization(self, desired_items, budget):
        """
        Optimize furniture selection within budget
        """
        total_cost = sum(item['price'] for item in desired_items)
        
        if total_cost <= budget:
            return {
                'optimal_set': desired_items,
                'total_cost': total_cost,
                'savings': budget - total_cost,
                'message': 'All items fit within budget'
            }
        
        # Need to find optimal combination
        items_sorted = sorted(desired_items, key=lambda x: x['priority'], reverse=True)
        
        optimal_set = []
        current_cost = 0
        
        for item in items_sorted:
            if current_cost + item['price'] <= budget:
                optimal_set.append(item)
                current_cost += item['price']
        
        # Suggest alternatives for items that didn't fit
        alternatives = []
        for item in items_sorted[len(optimal_set):]:
            alt = self._find_cheaper_alternative(item, budget - current_cost)
            if alt:
                alternatives.append(alt)
        
        return {
            'optimal_set': optimal_set,
            'total_cost': current_cost,
            'alternatives': alternatives,
            'message': f'Selected {len(optimal_set)} out of {len(desired_items)} items'
        }
    
    def _find_cheaper_alternative(self, item, remaining_budget):
        """Find a cheaper alternative for an item"""
        # In production, query database for similar items at lower price
        if item['price'] * 0.7 <= remaining_budget:
            return {
                'original': item['name'],
                'alternative': f"Budget {item['name']}",
                'price': item['price'] * 0.7,
                'savings': item['price'] * 0.3
            }
        return None