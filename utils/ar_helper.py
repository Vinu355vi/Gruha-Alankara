import json
import numpy as np

class ARHelper:
    def __init__(self):
        self.models_path = 'static/models/'
        self.supported_formats = ['.glb', '.gltf', '.obj', '.fbx']
    
    def prepare_model_for_ar(self, model_name, scale=1.0, rotation=[0, 0, 0]):
        """
        Prepare 3D model for AR placement
        """
        model_config = {
            'name': model_name,
            'url': f'{self.models_path}{model_name}.glb',
            'scale': scale,
            'rotation': rotation,
            'position': [0, 0, 0],
            'animation': 'idle',
            'interaction': True
        }
        
        return model_config
    
    def calculate_placement(self, room_dimensions, furniture_dimensions, position_constraints=None):
        """
        Calculate optimal furniture placement in AR space
        """
        room_width, room_length, room_height = room_dimensions
        furniture_width, furniture_length, furniture_height = furniture_dimensions
        
        # Calculate available space
        available_width = room_width - furniture_width
        available_length = room_length - furniture_length
        
        # Find valid positions
        valid_positions = []
        
        if position_constraints:
            # Respect constraints (e.g., against wall, center, etc.)
            if 'against_wall' in position_constraints:
                # Place against wall
                positions = [
                    [furniture_width/2, 0, furniture_length/2],
                    [room_width - furniture_width/2, 0, furniture_length/2],
                    [furniture_width/2, 0, room_length - furniture_length/2],
                    [room_width - furniture_width/2, 0, room_length - furniture_length/2]
                ]
                valid_positions.extend(positions)
            
            if 'center' in position_constraints:
                valid_positions.append([room_width/2, 0, room_length/2])
        else:
            # Generate grid of possible positions
            step = 0.5  # 0.5 meter steps
            x_positions = np.arange(furniture_width/2, room_width - furniture_width/2, step)
            z_positions = np.arange(furniture_length/2, room_length - furniture_length/2, step)
            
            for x in x_positions:
                for z in z_positions:
                    valid_positions.append([float(x), 0, float(z)])
        
        return valid_positions
    
    def generate_ar_session_data(self, furniture_items, room_id=None):
        """
        Generate AR session data for multiple furniture items
        """
        session_data = {
            'session_id': self._generate_session_id(),
            'room_id': room_id,
            'furniture': [],
            'environment': {
                'lighting': 'auto',
                'shadow': True,
                'reflection': True
            }
        }
        
        for item in furniture_items:
            furniture_data = {
                'id': item.get('id'),
                'model': self.prepare_model_for_ar(
                    item['model_name'],
                    scale=item.get('scale', 1.0),
                    rotation=item.get('rotation', [0, 0, 0])
                ),
                'position': item.get('position', [0, 0, 0]),
                'interactive': True
            }
            session_data['furniture'].append(furniture_data)
        
        return session_data
    
    def _generate_session_id(self):
        """
        Generate unique session ID
        """
        import uuid
        return str(uuid.uuid4())
    
    def process_ar_interaction(self, session_id, interaction_type, data):
        """
        Process AR interaction (placement, rotation, scale, etc.)
        """
        response = {
            'session_id': session_id,
            'interaction': interaction_type,
            'success': True,
            'data': {}
        }
        
        if interaction_type == 'place':
            response['data'] = self._handle_placement(data)
        elif interaction_type == 'rotate':
            response['data'] = self._handle_rotation(data)
        elif interaction_type == 'scale':
            response['data'] = self._handle_scaling(data)
        elif interaction_type == 'remove':
            response['data'] = self._handle_removal(data)
        
        return response
    
    def _handle_placement(self, data):
        """Handle furniture placement"""
        return {
            'position': data.get('position', [0, 0, 0]),
            'validation': self._validate_placement(data)
        }
    
    def _handle_rotation(self, data):
        """Handle furniture rotation"""
        current_rotation = data.get('current_rotation', [0, 0, 0])
        delta = data.get('delta', [0, 0, 0])
        
        new_rotation = [
            current_rotation[0] + delta[0],
            current_rotation[1] + delta[1],
            current_rotation[2] + delta[2]
        ]
        
        return {'rotation': new_rotation}
    
    def _handle_scaling(self, data):
        """Handle furniture scaling"""
        current_scale = data.get('current_scale', 1.0)
        delta = data.get('delta', 0)
        
        new_scale = max(0.5, min(2.0, current_scale + delta))
        
        return {'scale': new_scale}
    
    def _handle_removal(self, data):
        """Handle furniture removal"""
        return {'removed': True}
    
    def _validate_placement(self, data):
        """Validate if placement position is valid"""
        position = data.get('position', [0, 0, 0])
        existing_items = data.get('existing_items', [])
        
        # Check for collisions with existing items
        for item in existing_items:
            item_pos = item.get('position', [0, 0, 0])
            distance = np.sqrt(
                (position[0] - item_pos[0])**2 + 
                (position[2] - item_pos[2])**2
            )
            
            if distance < 1.0:  # Minimum distance of 1 meter
                return {
                    'valid': False,
                    'reason': 'Too close to existing furniture'
                }
        
        return {'valid': True}
    
    def export_ar_config(self, session_data, format='json'):
        """
        Export AR configuration for use in mobile apps
        """
        if format == 'json':
            return json.dumps(session_data, indent=2)
        elif format == 'xml':
            # Convert to XML format
            return self._convert_to_xml(session_data)
        else:
            return session_data
    
    def _convert_to_xml(self, data):
        """Convert AR data to XML format"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element('ar_session')
        root.set('id', data['session_id'])
        
        if data.get('room_id'):
            room = ET.SubElement(root, 'room')
            room.set('id', data['room_id'])
        
        furniture = ET.SubElement(root, 'furniture')
        for item in data.get('furniture', []):
            furniture_item = ET.SubElement(furniture, 'item')
            furniture_item.set('id', str(item.get('id', '')))
            
            model = ET.SubElement(furniture_item, 'model')
            model.text = item['model']['name']
            
            position = ET.SubElement(furniture_item, 'position')
            position.text = ','.join(map(str, item['position']))
        
        return ET.tostring(root, encoding='unicode')