import numpy as np
from sklearn.neighbors import NearestNeighbors
import json

class RecommendationModel:
    def __init__(self):
        self.furniture_database = self._load_furniture_database()
        self.knn_model = None
        self._train_model()
    
    def _load_furniture_database(self):
        """
        Load furniture database
        In production, this would come from a real database
        """
        return [
            {'id': 1, 'name': 'Modern Sofa', 'style': 'modern', 'price': 599, 
             'dimensions': [84, 38, 33], 'color': 'gray', 'material': 'fabric'},
            {'id': 2, 'name': 'Sectional Sofa', 'style': 'contemporary', 'price': 899,
             'dimensions': [96, 60, 35], 'color': 'beige', 'material': 'leather'},
            {'id': 3, 'name': 'Coffee Table', 'style': 'modern', 'price': 199,
             'dimensions': [48, 24, 18], 'color': 'brown', 'material': 'wood'},
            {'id': 4, 'name': 'Dining Table', 'style': 'traditional', 'price': 399,
             'dimensions': [72, 36, 30], 'color': 'dark brown', 'material': 'wood'},
            {'id': 5, 'name': 'Floor Lamp', 'style': 'modern', 'price': 89,
             'dimensions': [15, 15, 58], 'color': 'black', 'material': 'metal'},
            {'id': 6, 'name': 'Area Rug', 'style': 'bohemian', 'price': 249,
             'dimensions': [96, 120, 1], 'color': 'multicolor', 'material': 'wool'}
        ]
    
    def _train_model(self):
        """
        Train KNN model for furniture recommendations
        """
        # Extract features for training
        features = []
        for item in self.furniture_database:
            # Create feature vector: price, dimensions, style encoding
            feature_vector = [
                item['price'] / 1000,  # Normalize price
                item['dimensions'][0] / 100,  # Normalize width
                item['dimensions'][1] / 100,  # Normalize length
                item['dimensions'][2] / 100,  # Normalize height
                self._encode_style(item['style']),
                self._encode_material(item['material'])
            ]
            features.append(feature_vector)
        
        features = np.array(features)
        
        # Train KNN model
        self.knn_model = NearestNeighbors(n_neighbors=5, metric='euclidean')
        self.knn_model.fit(features)
    
    def _encode_style(self, style):
        """
        Encode style as numerical value
        """
        style_map = {
            'modern': 1.0,
            'contemporary': 0.8,
            'traditional': 0.6,
            'minimalist': 0.4,
            'bohemian': 0.2,
            'industrial': 0.0
        }
        return style_map.get(style, 0.5)
    
    def _encode_material(self, material):
        """
        Encode material as numerical value
        """
        material_map = {
            'fabric': 1.0,
            'leather': 0.8,
            'wood': 0.6,
            'metal': 0.4,
            'glass': 0.2,
            'wool': 0.0
        }
        return material_map.get(material, 0.5)
    
    def get_recommendations(self, user_preferences, n_recommendations=5):
        """
        Get furniture recommendations based on user preferences
        """
        # Create query vector from user preferences
        query = [
            user_preferences.get('budget', 500) / 1000,
            user_preferences.get('width', 50) / 100,
            user_preferences.get('length', 50) / 100,
            user_preferences.get('height', 30) / 100,
            self._encode_style(user_preferences.get('style', 'modern')),
            self._encode_material(user_preferences.get('material', 'fabric'))
        ]
        
        query = np.array(query).reshape(1, -1)
        
        # Find nearest neighbors
        distances, indices = self.knn_model.kneighbors(query, n_neighbors=n_recommendations)
        
        # Get recommended items
        recommendations = []
        for idx in indices[0]:
            item = self.furniture_database[idx].copy()
            item['similarity_score'] = float(1 - distances[0][list(indices[0]).index(idx)] / 10)
            recommendations.append(item)
        
        return recommendations
    
    def get_similar_items(self, item_id, n_similar=3):
        """
        Get items similar to a given item
        """
        # Find the item in database
        target_item = None
        for item in self.furniture_database:
            if item['id'] == item_id:
                target_item = item
                break
        
        if not target_item:
            return []
        
        # Create feature vector for target item
        target_features = np.array([[
            target_item['price'] / 1000,
            target_item['dimensions'][0] / 100,
            target_item['dimensions'][1] / 100,
            target_item['dimensions'][2] / 100,
            self._encode_style(target_item['style']),
            self._encode_material(target_item['material'])
        ]])
        
        # Find similar items
        distances, indices = self.knn_model.kneighbors(target_features, n_neighbors=n_similar + 1)
        
        # Skip the first one (it's the item itself)
        similar_items = []
        for i in range(1, len(indices[0])):
            idx = indices[0][i]
            item = self.furniture_database[idx].copy()
            item['similarity_score'] = float(1 - distances[0][i] / 10)
            similar_items.append(item)
        
        return similar_items
    
    def filter_by_room_type(self, room_type, budget_range=None):
        """
        Filter furniture by room type
        """
        room_furniture_map = {
            'living': ['sofa', 'coffee table', 'tv stand', 'bookshelf'],
            'bedroom': ['bed', 'nightstand', 'dresser', 'wardrobe'],
            'dining': ['dining table', 'dining chair', 'buffet'],
            'office': ['desk', 'office chair', 'bookshelf']
        }
        
        filtered_items = []
        for item in self.furniture_database:
            # Check if item name contains any room-appropriate keywords
            if any(keyword in item['name'].lower() for keyword in room_furniture_map.get(room_type, [])):
                if budget_range:
                    min_budget, max_budget = budget_range
                    if min_budget <= item['price'] <= max_budget:
                        filtered_items.append(item)
                else:
                    filtered_items.append(item)
        
        return filtered_items
    
    def get_price_estimate(self, furniture_list):
        """
        Estimate total price for a list of furniture
        """
        total = 0
        breakdown = []
        
        for furniture_name in furniture_list:
            # Find matching item in database
            for item in self.furniture_database:
                if furniture_name.lower() in item['name'].lower():
                    total += item['price']
                    breakdown.append({
                        'name': item['name'],
                        'price': item['price']
                    })
                    break
        
        return {
            'total': total,
            'breakdown': breakdown,
            'estimated_tax': total * 0.08,
            'estimated_shipping': 49 if total < 500 else 0,
            'grand_total': total + (total * 0.08) + (49 if total < 500 else 0)
        }