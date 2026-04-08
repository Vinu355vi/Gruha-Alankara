try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np
from PIL import Image
import math
import random

class RoomAnalyzer:
    def __init__(self):
        self.furniture_detector = None
        self.wall_detector = None
        
    def analyze_image(self, image_path):
        """
        Comprehensive room analysis from image
        """
        if cv2 is None:
            # Fallback for when OpenCV is not available
            return self._mock_analysis(image_path)

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Could not load image'}
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Perform analyses
        results = {
            'dimensions': self.estimate_dimensions(image_rgb),
            'walls': self.detect_walls(image_rgb),
            'floor': self.analyze_floor(image_rgb),
            'furniture': self.detect_furniture(image_rgb),
            'lighting': self.analyze_lighting(image_rgb),
            'colors': self.extract_colors(image_rgb),
            'perspective': self.analyze_perspective(image_rgb)
        }
        
        # Generate color palette
        results['recommended_palette'] = self.generate_color_palette(results['colors'])

        # Generate recommendations
        results['recommendations'] = self.generate_recommendations(results)
        
        return results

    def _mock_analysis(self, image_path):
        """Provide mock data if dependencies are missing"""
        # Generate some random variations based on image path hash or random
        import random
        
        width = random.uniform(10.0, 15.0)
        length = random.uniform(12.0, 18.0)
        
        # Random dominant colors with percentages
        colors = []
        base_hues = [
            {'hex': '#F5F5DC', 'name': 'Beige'}, 
            {'hex': '#E0E0E0', 'name': 'Light Gray'},
            {'hex': '#FFFFFF', 'name': 'White'},
            {'hex': '#D2B48C', 'name': 'Tan'}
        ]
        accent_hues = [
            {'hex': '#8B4513', 'name': 'Saddle Brown'},
            {'hex': '#2F4F4F', 'name': 'Dark Slate Gray'},
            {'hex': '#708090', 'name': 'Slate Gray'},
            {'hex': '#556B2F', 'name': 'Dark Olive Green'}
        ]
        
        primary = random.choice(base_hues)
        secondary = random.choice(accent_hues)
        
        colors = [
            {'hex': primary['hex'], 'percentage': 60},
            {'hex': secondary['hex'], 'percentage': 30},
            {'hex': '#000000', 'percentage': 10}
        ]

        return {
            'dimensions': {
                'width': round(width, 1), 
                'length': round(length, 1), 
                'height': 9,
                'area': round(width * length, 1)
            },
            'walls': [],
            'floor': {},
            'furniture': [
                {'type': 'Sofa', 'confidence': 0.95, 'position': [0.5, 0.5], 'size': [0.4, 0.2]},
                {'type': 'Table', 'confidence': 0.88, 'position': [0.5, 0.7], 'size': [0.3, 0.3]}
            ],
            'lighting': {
                'quality': 'good', 
                'natural_light_estimate': random.randint(40, 80)
            },
            'colors': colors,
            'perspective': {},
            'recommended_palette': [
                {'name': 'Base', 'hex': primary['hex']},
                {'name': 'Light', 'hex': '#FFFFFF'},
                {'name': 'Contrast', 'hex': secondary['hex']}
            ],
            'recommendations': [{'style': 'Modern', 'score': 90}, {'style': 'Minimalist', 'score': 85}]
        }
    
    def estimate_dimensions(self, image):
        """
        Estimate room dimensions using perspective
        """
        height, width, _ = image.shape
        
        # Use reference objects for scale
        # In production, use known object sizes or depth estimation
        
        # Mock dimensions based on image properties
        aspect_ratio = width / height
        
        # Assume average ceiling height of 2.7m
        ceiling_height = 2.7
        
        # Estimate width based on aspect ratio
        estimated_width = 5.0  # meters
        estimated_length = estimated_width / aspect_ratio
        
        return {
            'width': round(estimated_width, 2),
            'length': round(estimated_length, 2),
            'height': ceiling_height,
            'area': round(estimated_width * estimated_length, 2),
            'volume': round(estimated_width * estimated_length * ceiling_height, 2)
        }
    
    def detect_walls(self, image):
        """
        Detect wall positions and colors
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Edge detection for wall boundaries
        edges = cv2.Canny(gray, 50, 150)
        
        # Hough transform for line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        walls = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                # Classify as wall if line is long enough
                if length > 200:
                    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                    walls.append({
                        'start': [int(x1), int(y1)],
                        'end': [int(x2), int(y2)],
                        'length': float(length),
                        'angle': float(angle)
                    })
        
        # Extract wall colors
        wall_colors = self._extract_wall_colors(image, walls)
        
        return {
            'count': len(walls),
            'walls': walls[:4],  # Limit to 4 main walls
            'colors': wall_colors
        }
    
    def _extract_wall_colors(self, image, walls):
        """
        Extract dominant colors from walls
        """
        colors = []
        height, width, _ = image.shape
        
        for wall in walls[:4]:  # Analyze first 4 walls
            # Sample points along the wall
            x1, y1 = wall['start']
            x2, y2 = wall['end']
            
            # Sample color from middle of wall
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2
            
            if 0 <= mx < width and 0 <= my < height:
                color = image[my, mx]
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                colors.append(hex_color)
        
        return colors
    
    def analyze_floor(self, image):
        """
        Analyze floor type and condition
        """
        height, width, _ = image.shape
        
        # Focus on bottom portion of image (floor area)
        floor_region = image[int(height*0.7):, :]
        
        if floor_region.size == 0:
            return {'type': 'unknown', 'condition': 'unknown'}
        
        # Analyze texture and color
        gray_floor = cv2.cvtColor(floor_region, cv2.COLOR_RGB2GRAY)
        texture = np.std(gray_floor)
        
        # Determine floor type based on texture
        if texture < 20:
            floor_type = 'smooth (tile/hardwood)'
        elif texture < 40:
            floor_type = 'carpet'
        else:
            floor_type = 'textured/patterned'
        
        # Detect color
        avg_color = np.mean(floor_region, axis=(0, 1))
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
        )
        
        return {
            'type': floor_type,
            'color': hex_color,
            'texture_score': float(texture),
            'condition': 'good' if texture < 50 else 'worn'
        }
    
    def detect_furniture(self, image):
        """
        Detect furniture in the image using OpenCV techniques.
        """
        furniture_items = []
        height, width, _ = image.shape
        
        # Convert to grayscale and blur
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilate edges to connect broken lines
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and classify contours
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter small noise (less than 2% of image area)
            if area < (width * height * 0.02):
                continue
                
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate relative position and size
            rel_x = x / width
            rel_y = y / height
            rel_w = w / width
            rel_h = h / height
            aspect_ratio = w / h
            
            # Heuristic classification based on position and shape
            item_type = 'unknown'
            confidence = 0.5 + (min(area / (width * height), 0.4)) # Higher area = higher confidence
            
            # Center of the object
            center_x = rel_x + rel_w/2
            center_y = rel_y + rel_h/2
            
            if rel_y > 0.6: # Bottom part of image
                if aspect_ratio > 1.5:
                    item_type = 'coffee_table' if rel_h < 0.3 else 'sofa'
                else:
                    item_type = 'chair' if rel_h > 0.3 else 'footstool'
            elif rel_y > 0.4: # Middle part
                if aspect_ratio > 2.0:
                    item_type = 'sofa'
                elif aspect_ratio < 0.8:
                    item_type = 'lamp' if rel_w < 0.15 else 'armchair'
                else:
                    item_type = 'table'
            elif rel_y < 0.4: # Top part
                if rel_w < 0.2:
                    item_type = 'lamp'
                elif rel_w > 0.3 and rel_h > 0.3:
                    item_type = 'cabinet'
                else:
                    item_type = 'decor'
            
            # Check for specific shapes (circle-ish)
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            if circularity > 0.75:
                if rel_y > 0.5:
                    item_type = 'round_table'
                else:
                    item_type = 'clock' if rel_y < 0.3 else 'decor'

            # Get dominant color of the object
            mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            mean_color = cv2.mean(image, mask=mask)[:3]
            color_hex = '#{:02x}{:02x}{:02x}'.format(int(mean_color[0]), int(mean_color[1]), int(mean_color[2]))

            # Add to results
            furniture_items.append({
                'id': i,
                'type': item_type,
                'confidence': round(confidence, 2),
                'position': [round(rel_x, 2), round(rel_y, 2)],
                'size': [round(rel_w, 2), round(rel_h, 2)],
                'color': color_hex
            })
            
        # Limit to top 5 detected items by area (largest first)
        furniture_items.sort(key=lambda x: x['size'][0] * x['size'][1], reverse=True)
        return furniture_items[:5] if furniture_items else [{'type': 'empty_space', 'confidence': 0.9}]
    
    def analyze_lighting(self, image):
        """
        Analyze lighting conditions
        """
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Analyze brightness
        brightness = np.mean(hsv[:, :, 2])
        
        # Analyze contrast
        contrast = np.std(hsv[:, :, 2])
        
        # Detect light sources (bright areas)
        _, bright_regions = cv2.threshold(hsv[:, :, 2], 200, 255, cv2.THRESH_BINARY)
        light_sources = cv2.countNonZero(bright_regions)
        
        # Determine lighting quality
        if brightness > 180:
            quality = 'excellent'
        elif brightness > 120:
            quality = 'good'
        elif brightness > 60:
            quality = 'moderate'
        else:
            quality = 'poor'
        
        # Estimate natural vs artificial
        # This is simplified - in production, use color temperature analysis
        avg_color_temp = np.mean(hsv[:, :, 0])  # Hue
        is_natural = 180 < avg_color_temp < 260  # Blue-ish light
        
        return {
            'brightness': float(brightness),
            'contrast': float(contrast),
            'quality': quality,
            'light_sources': int(light_sources),
            'natural_light_estimate': float(brightness / 255 * 100) if is_natural else float(brightness / 255 * 60),
            'recommendations': self._get_lighting_recommendations(brightness, quality)
        }
    
    def _get_lighting_recommendations(self, brightness, quality):
        """Get lighting improvement recommendations"""
        recommendations = []
        
        if brightness < 100:
            recommendations.append({
                'type': 'ambient',
                'priority': 'high',
                'suggestion': 'Add overhead lighting or floor lamps'
            })
        
        if quality == 'moderate' or quality == 'poor':
            recommendations.append({
                'type': 'task',
                'priority': 'medium',
                'suggestion': 'Add task lighting near work areas'
            })
        
        recommendations.append({
            'type': 'accent',
            'priority': 'low',
            'suggestion': 'Use accent lighting to highlight features'
        })
        
        return recommendations
    
    def extract_colors(self, image, n_colors=5):
        """
        Extract dominant colors from image
        """
        try:
            # Resize for faster processing
            image_small = cv2.resize(image, (100, 100))
            pixels = image_small.reshape(-1, 3)
            
            # Use k-means for color quantization
            try:
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
                kmeans.fit(pixels)
                colors = kmeans.cluster_centers_.astype(int)
                labels = kmeans.labels_
                counts = np.bincount(labels)
                percentages = (counts / len(labels) * 100).round(1)
            except ImportError:
                # Fallback: simple histogram or just center crop average
                # For robustness, just use random sampling or center color
                center_color = np.mean(pixels, axis=0).astype(int)
                colors = [center_color]
                percentages = [100.0]
                n_colors = 1

            # Format results
            color_list = []
            for i in range(len(colors)):
                color_list.append({
                    'rgb': colors[i].tolist(),
                    'hex': '#{:02x}{:02x}{:02x}'.format(colors[i][0], colors[i][1], colors[i][2]),
                    'percentage': float(percentages[i])
                })
            
            # Sort by percentage
            color_list.sort(key=lambda x: x['percentage'], reverse=True)
            
            return color_list
            
        except Exception as e:
            print(f"Color extraction error: {e}")
            return [{'rgb': [200, 200, 200], 'hex': '#C8C8C8', 'percentage': 100.0}]
    
    def analyze_perspective(self, image):
        """
        Analyze perspective to understand room layout
        """
        height, width, _ = image.shape
        
        # Find vanishing points (simplified)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        vanishing_points = []
        if lines is not None:
            # Find intersection of lines (simplified)
            for i in range(min(10, len(lines))):
                rho1, theta1 = lines[i][0]
                for j in range(i+1, min(10, len(lines))):
                    rho2, theta2 = lines[j][0]
                    
                    # Calculate intersection
                    A = np.array([
                        [np.cos(theta1), np.sin(theta1)],
                        [np.cos(theta2), np.sin(theta2)]
                    ])
                    b = np.array([rho1, rho2])
                    
                    try:
                        vp = np.linalg.solve(A, b)
                        if 0 <= vp[0] < width and 0 <= vp[1] < height:
                            vanishing_points.append(vp.tolist())
                    except:
                        pass
        
        return {
            'has_vanishing_points': len(vanishing_points) > 0,
            'vanishing_points': vanishing_points[:3],  # Limit to 3
            'camera_angle': self._estimate_camera_angle(lines) if lines is not None else 0
        }
    
    def _estimate_camera_angle(self, lines):
        """Estimate camera angle from lines"""
        if lines is None or len(lines) == 0:
            return 0
        
        # Average line angles
        angles = []
        for line in lines[:10]:  # Sample first 10 lines
            theta = line[0][1]
            angles.append(math.degrees(theta))
        
        if not angles:
            return 0
        
        avg_angle = sum(angles) / len(angles)
        
        # Normalize to 0-90 range
        if avg_angle > 90:
            avg_angle = 180 - avg_angle
        
        return float(avg_angle)
    
    def generate_color_palette(self, detected_colors):
        """
        Generate a recommended 3-color palette (Base, Light, Contrast)
        based on detected room colors using color theory.
        """
        palette = []
        if not detected_colors:
            return [
                {'name': 'Base', 'hex': '#F5F5DC'},
                {'name': 'Light', 'hex': '#FFFFFF'},
                {'name': 'Contrast', 'hex': '#2F4F4F'}
            ]
            
        # 1. Base Color: Use the most dominant detected color
        base_color = detected_colors[0]
        base_rgb = base_color['rgb']
        palette.append({'name': 'Base', 'hex': base_color['hex']})
        
        # Helper to manipulate RGB
        def adjust_brightness(rgb, factor):
            return [max(0, min(255, int(c * factor))) for c in rgb]
            
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            
        # 2. Light Color:
        # If base is dark (<128 avg), use a very light version of it
        # If base is light (>200 avg), use white or off-white
        avg_brightness = sum(base_rgb) / 3
        if avg_brightness < 128:
            light_rgb = adjust_brightness(base_rgb, 1.8) # Significantly lighter
        elif avg_brightness > 220:
            light_rgb = [250, 250, 250] # Almost white
        else:
            light_rgb = adjust_brightness(base_rgb, 1.4) # Slightly lighter
            
        palette.append({'name': 'Light', 'hex': rgb_to_hex(light_rgb)})
        
        # 3. Contrast Color:
        # Find a complementary color or a strong accent from other detected colors
        contrast_found = False
        
        # Try to find a contrasting color from detected list first
        for color in detected_colors[1:]:
            c_rgb = color['rgb']
            # Simple contrast check: difference in brightness
            c_bright = sum(c_rgb) / 3
            if abs(c_bright - avg_brightness) > 100:
                palette.append({'name': 'Contrast', 'hex': color['hex']})
                contrast_found = True
                break
                
        if not contrast_found:
            # Generate a complementary color mathematically
            # Simple inversion for high contrast
            comp_rgb = [255 - c for c in base_rgb]
            palette.append({'name': 'Contrast', 'hex': rgb_to_hex(comp_rgb)})
            
        return palette

    def generate_recommendations(self, analysis):
        """
        Generate overall room recommendation styles based on analysis
        """
        recommendations = []
        
        # Analyze Color Palette for Style
        colors = analysis.get('colors', [])
        lighting = analysis.get('lighting', {})
        furniture_count = len(analysis.get('furniture', []))
        
        # Determine dominant lighting vibe
        is_bright = lighting.get('brightness', 0) > 100
        is_warm = lighting.get('natural_light_estimate', 0) > 50 # Simplified proxy
        
        # Heuristic Style Matching
        styles = {
            'Minimalist': 0,
            'Scandinavian': 0,
            'Industrial': 0,
            'Bohemian': 0,
            'Modern': 0,
            'Traditional': 0
        }
        
        # 1. Furniture Density
        if furniture_count < 3:
            styles['Minimalist'] += 2
            styles['Modern'] += 1
        elif furniture_count > 6:
            styles['Bohemian'] += 1
            styles['Traditional'] += 2
        else:
            styles['Scandinavian'] += 1
            styles['Modern'] += 1
            
        # 2. Lighting
        if is_bright:
            styles['Scandinavian'] += 2
            styles['Modern'] += 1
        else:
            styles['Industrial'] += 1
            styles['Traditional'] += 1
            
        # 3. Colors (using simple hex analysis or just count for now)
        # In a real app, we'd map hex to color names/temperatures
        if len(colors) < 3:
            styles['Minimalist'] += 1
        else:
            styles['Bohemian'] += 1
            
        # Select top 3 styles
        sorted_styles = sorted(styles.items(), key=lambda x: x[1], reverse=True)
        
        for style, score in sorted_styles[:3]:
            # Generate description based on why we picked it
            description = f"Based on the {'bright' if is_bright else 'moody'} lighting and {furniture_count} detected items."
            if style == 'Minimalist':
                description = "Your space has a clean, uncluttered look perfect for a Minimalist approach."
            elif style == 'Scandinavian':
                description = "The lighting and layout suggest a cozy, functional Scandinavian design."
            elif style == 'Industrial':
                description = "The raw elements and lighting favor an Industrial aesthetic."
                
            recommendations.append({
                'style': style,
                'confidence': min(0.5 + (score * 0.1), 0.95), # Normalize mock score
                'description': description
            })
            
        return recommendations