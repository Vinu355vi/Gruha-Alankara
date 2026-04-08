// Design Recommendations JavaScript - Complete File
class DesignRecommender {
    constructor() {
        this.preferences = {};
        this.recommendations = null;
        this.currentDesign = null;
        this.savedDesigns = [];
        this.init();
    }
    
    init() {
        this.loadSavedDesigns();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Listen for preference form submission
        const prefForm = document.getElementById('preferenceForm');
        if (prefForm) {
            prefForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handlePreferenceSubmit(e);
            });
        }
        
        // Listen for style selection
        document.querySelectorAll('.style-option').forEach(option => {
            option.addEventListener('click', (e) => {
                this.selectStyle(e.target.dataset.style);
            });
        });
        
        // Listen for color selection
        document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', (e) => {
                this.selectColor(e.target.dataset.color);
            });
        });
    }
    
    async handlePreferenceSubmit(event) {
        const formData = new FormData(event.target);
        this.preferences = Object.fromEntries(formData.entries());
        
        // Show loading state
        this.showLoading();
        
        try {
            // Get recommendations from AI
            this.recommendations = await this.getRecommendations(this.preferences);
            
            // Hide loading and show results
            this.hideLoading();
            this.displayRecommendations(this.recommendations);
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to get recommendations. Please try again.');
            console.error('Recommendation error:', error);
        }
    }
    
    async getRecommendations(preferences) {
        // Simulate API call to AI model
        return new Promise((resolve) => {
            setTimeout(() => {
                const recommendations = this.generateMockRecommendations(preferences);
                resolve(recommendations);
            }, 2000);
        });
    }
    
    generateMockRecommendations(preferences) {
        const roomType = preferences.room_type || 'living';
        const style = preferences.style || 'modern';
        const colorPref = preferences.color || 'neutral';
        const budget = preferences.budget || 'moderate';
        
        // Generate color palette
        const colorPalette = this.generateColorPalette(colorPref, style);
        
        // Generate furniture layout
        const furniture = this.generateFurnitureList(roomType, style);
        
        // Generate layout
        const layout = this.generateLayout(preferences, furniture);
        
        // Generate shopping list
        const shopping = this.generateShoppingList(furniture, budget);
        
        // Calculate costs
        const estimatedCost = this.calculateEstimatedCost(shopping);
        
        // Generate style matches
        const styleMatches = this.generateStyleMatches(roomType, style);
        
        return {
            colorPalette,
            furniture,
            layout,
            shopping,
            estimatedCost,
            styleMatches,
            timestamp: new Date().toISOString()
        };
    }
    
    generateColorPalette(preference, style) {
        const palettes = {
            neutral: {
                modern: ['#F5F5F5', '#E8E8E8', '#D3D3D3', '#BEBEBE', '#A9A9A9'],
                minimalist: ['#FFFFFF', '#FAFAFA', '#F5F5F5', '#EEEEEE', '#E0E0E0'],
                scandinavian: ['#F9F9F9', '#F0F0F0', '#E8E8E8', '#E0E0E0', '#D3D3D3'],
                industrial: ['#2C3E50', '#34495E', '#7F8C8D', '#BDC3C7', '#ECF0F1']
            },
            warm: {
                modern: ['#FF6B6B', '#FF8E53', '#FFB347', '#FFD700', '#FFA07A'],
                minimalist: ['#F4A460', '#DEB887', '#D2B48C', '#BC8F8F', '#A0522D'],
                scandinavian: ['#FFE4B5', '#FFDAB9', '#FFE4C4', '#FFDEAD', '#F5DEB3'],
                industrial: ['#8B4513', '#A0522D', '#CD853F', '#D2691E', '#B8860B']
            },
            cool: {
                modern: ['#4A90E2', '#50C878', '#20B2AA', '#4682B4', '#5F9EA0'],
                minimalist: ['#B0E0E6', '#ADD8E6', '#87CEEB', '#87CEFA', '#00BFFF'],
                scandinavian: ['#E0FFFF', '#AFEEEE', '#7FFFD4', '#40E0D0', '#48D1CC'],
                industrial: ['#2F4F4F', '#708090', '#778899', '#B0C4DE', '#C0C0C0']
            },
            bold: {
                modern: ['#FF1493', '#FF4500', '#9400D3', '#00CED1', '#FFD700'],
                minimalist: ['#DC143C', '#B22222', '#8B0000', '#800000', '#A52A2A'],
                scandinavian: ['#FF69B4', '#FFB6C1', '#FFC0CB', '#FFDAB9', '#FFE4E1'],
                industrial: ['#8B0000', '#B22222', '#DC143C', '#FF0000', '#CD5C5C']
            },
            pastel: {
                modern: ['#FFB6C1', '#FFDAB9', '#E6E6FA', '#B0E0E6', '#98FB98'],
                minimalist: ['#FFF0F5', '#FFF5EE', '#F0FFF0', '#F5FFFA', '#F0F8FF'],
                scandinavian: ['#FFE4E1', '#FFDAB9', '#FFFACD', '#E6E6FA', '#F0E68C'],
                industrial: ['#DDA0DD', '#EE82EE', '#DA70D6', '#FF00FF', '#FF1493']
            },
            monochrome: {
                modern: ['#000000', '#333333', '#666666', '#999999', '#CCCCCC'],
                minimalist: ['#1A1A1A', '#4D4D4D', '#808080', '#B3B3B3', '#E6E6E6'],
                scandinavian: ['#2C2C2C', '#595959', '#858585', '#B2B2B2', '#D9D9D9'],
                industrial: ['#0A0A0A', '#3A3A3A', '#6A6A6A', '#9A9A9A', '#CACACA']
            }
        };
        
        return palettes[preference]?.[style] || palettes.neutral.modern;
    }
    
    generateFurnitureList(roomType, style) {
        const furnitureByRoom = {
            living: [
                { id: 1, name: '3-Seater Fabric Sofa', dimensions: '84" x 38" x 33"', price: 599, store: 'IKEA', category: 'sofa', style: 'modern', image: '/static/images/furniture/modern-sofa.jpg', rating: 4.5, material: 'fabric' },
                { id: 2, name: 'Glass Coffee Table', dimensions: '48" x 24" x 18"', price: 199, store: 'Wayfair', category: 'table', style: 'modern', image: '/static/images/furniture/coffee-table.jpg', rating: 4.3, material: 'glass' },
                { id: 3, name: 'TV Stand with Storage', dimensions: '60" x 20" x 24"', price: 299, store: 'Amazon', category: 'tv_stand', style: 'modern', image: '/static/images/furniture/tv-stand.jpg', rating: 4.7, material: 'wood' },
                { id: 4, name: 'Area Rug - Modern Pattern', dimensions: '8\' x 10\'', price: 249, store: 'Home Depot', category: 'rug', style: 'modern', image: '/static/images/furniture/rug.jpg', rating: 4.2, material: 'wool' },
                { id: 5, name: 'Arc Floor Lamp', dimensions: '58" H', price: 89, store: 'Target', category: 'lamp', style: 'modern', image: '/static/images/furniture/lamp.jpg', rating: 4.8, material: 'metal' },
                { id: 6, name: 'Accent Armchair', dimensions: '32" x 34" x 30"', price: 299, store: 'Wayfair', category: 'chair', style: 'modern', image: '/static/images/furniture/armchair.jpg', rating: 4.4, material: 'velvet' }
            ],
            bedroom: [
                { id: 7, name: 'Queen Platform Bed', dimensions: '63" x 84" x 48"', price: 499, store: 'IKEA', category: 'bed', style: 'modern', image: '/static/images/furniture/bed.jpg', rating: 4.6, material: 'wood' },
                { id: 8, name: 'Nightstand with Drawer', dimensions: '24" x 18" x 24"', price: 129, store: 'Wayfair', category: 'nightstand', style: 'modern', image: '/static/images/furniture/nightstand.jpg', rating: 4.3, material: 'wood' },
                { id: 9, name: '6-Drawer Dresser', dimensions: '60" x 20" x 36"', price: 399, store: 'Amazon', category: 'dresser', style: 'modern', image: '/static/images/furniture/dresser.jpg', rating: 4.5, material: 'wood' },
                { id: 10, name: 'Wardrobe Closet', dimensions: '72" x 24" x 72"', price: 599, store: 'Home Depot', category: 'wardrobe', style: 'modern', image: '/static/images/furniture/wardrobe.jpg', rating: 4.4, material: 'wood' },
                { id: 11, name: 'Bedside Table Lamp', dimensions: '24" H', price: 49, store: 'Target', category: 'lamp', style: 'modern', image: '/static/images/furniture/bedside-lamp.jpg', rating: 4.7, material: 'ceramic' }
            ],
            kitchen: [
                { id: 12, name: 'Kitchen Island with Storage', dimensions: '48" x 30" x 36"', price: 399, store: 'IKEA', category: 'island', style: 'modern', image: '/static/images/furniture/island.jpg', rating: 4.5, material: 'wood' },
                { id: 13, name: 'Bar Stools (Set of 2)', dimensions: '18" x 18" x 30"', price: 149, store: 'Wayfair', category: 'stool', style: 'modern', image: '/static/images/furniture/stool.jpg', rating: 4.3, material: 'metal' },
                { id: 14, name: 'Open Shelf Unit', dimensions: '36" x 12" x 72"', price: 199, store: 'Amazon', category: 'shelf', style: 'modern', image: '/static/images/furniture/shelf.jpg', rating: 4.4, material: 'wood' }
            ],
            dining: [
                { id: 15, name: 'Dining Table - Extendable', dimensions: '72" x 36" x 30"', price: 399, store: 'IKEA', category: 'table', style: 'modern', image: '/static/images/furniture/dining-table.jpg', rating: 4.6, material: 'wood' },
                { id: 16, name: 'Dining Chairs (Set of 4)', dimensions: '18" x 20" x 36"', price: 299, store: 'Wayfair', category: 'chair', style: 'modern', image: '/static/images/furniture/dining-chair.jpg', rating: 4.4, material: 'fabric' },
                { id: 17, name: 'Buffet Cabinet', dimensions: '60" x 18" x 36"', price: 449, store: 'Amazon', category: 'cabinet', style: 'modern', image: '/static/images/furniture/buffet.jpg', rating: 4.3, material: 'wood' }
            ],
            office: [
                { id: 18, name: 'Executive Desk', dimensions: '60" x 30" x 30"', price: 349, store: 'IKEA', category: 'desk', style: 'modern', image: '/static/images/furniture/desk.jpg', rating: 4.5, material: 'wood' },
                { id: 19, name: 'Ergonomic Office Chair', dimensions: '28" x 28" x 45"', price: 199, store: 'Wayfair', category: 'chair', style: 'modern', image: '/static/images/furniture/office-chair.jpg', rating: 4.7, material: 'mesh' },
                { id: 20, name: 'Bookshelf', dimensions: '36" x 12" x 72"', price: 149, store: 'Amazon', category: 'shelf', style: 'modern', image: '/static/images/furniture/bookshelf.jpg', rating: 4.4, material: 'wood' }
            ]
        };
        
        // Filter by style if needed
        let furniture = furnitureByRoom[roomType] || furnitureByRoom.living;
        if (style) {
            furniture = furniture.filter(item => item.style === style);
        }
        
        return furniture;
    }
    
    generateLayout(preferences, furniture) {
        const width = parseFloat(preferences.width) || 12;
        const length = parseFloat(preferences.length) || 14;
        
        // Generate grid layout
        const gridSize = 2; // 2 feet grid cells
        const cols = Math.floor(width / gridSize);
        const rows = Math.floor(length / gridSize);
        
        // Create zones
        const zones = this.generateZones(preferences.room_type, cols, rows);
        
        // Place furniture in zones
        const placements = [];
        furniture.forEach((item, index) => {
            const zone = zones[index % zones.length];
            const position = this.calculatePosition(zone, index, cols, rows);
            
            placements.push({
                item: item.name,
                zone: zone.name,
                position: position,
                rotation: this.calculateRotation(item.category, zone),
                dimensions: item.dimensions
            });
        });
        
        return {
            grid: {
                cols: cols,
                rows: rows,
                cellSize: gridSize,
                totalArea: width * length
            },
            zones: zones,
            placements: placements,
            trafficFlow: this.generateTrafficFlow(cols, rows)
        };
    }
    
    generateZones(roomType, cols, rows) {
        const zones = {
            living: [
                { name: 'Seating Area', x: Math.floor(cols * 0.2), y: Math.floor(rows * 0.3), width: Math.floor(cols * 0.4), height: Math.floor(rows * 0.4), color: '#FF6B6B' },
                { name: 'Entertainment', x: Math.floor(cols * 0.7), y: Math.floor(rows * 0.3), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.3), color: '#4A90E2' },
                { name: 'Reading Nook', x: Math.floor(cols * 0.1), y: Math.floor(rows * 0.7), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.2), color: '#50C878' }
            ],
            bedroom: [
                { name: 'Sleeping Area', x: Math.floor(cols * 0.3), y: Math.floor(rows * 0.2), width: Math.floor(cols * 0.4), height: Math.floor(rows * 0.3), color: '#9B59B6' },
                { name: 'Closet Area', x: Math.floor(cols * 0.7), y: Math.floor(rows * 0.1), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.3), color: '#F39C12' },
                { name: 'Dressing Area', x: Math.floor(cols * 0.1), y: Math.floor(rows * 0.5), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.3), color: '#1ABC9C' }
            ],
            kitchen: [
                { name: 'Cooking Zone', x: Math.floor(cols * 0.1), y: Math.floor(rows * 0.1), width: Math.floor(cols * 0.3), height: Math.floor(rows * 0.4), color: '#E67E22' },
                { name: 'Preparation', x: Math.floor(cols * 0.5), y: Math.floor(rows * 0.1), width: Math.floor(cols * 0.3), height: Math.floor(rows * 0.3), color: '#3498DB' },
                { name: 'Storage', x: Math.floor(cols * 0.7), y: Math.floor(rows * 0.5), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.3), color: '#2ECC71' }
            ],
            dining: [
                { name: 'Dining Area', x: Math.floor(cols * 0.3), y: Math.floor(rows * 0.3), width: Math.floor(cols * 0.4), height: Math.floor(rows * 0.4), color: '#E74C3C' },
                { name: 'Sideboard', x: Math.floor(cols * 0.7), y: Math.floor(rows * 0.3), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.2), color: '#8E44AD' }
            ],
            office: [
                { name: 'Work Zone', x: Math.floor(cols * 0.2), y: Math.floor(rows * 0.2), width: Math.floor(cols * 0.4), height: Math.floor(rows * 0.3), color: '#2980B9' },
                { name: 'Storage', x: Math.floor(cols * 0.7), y: Math.floor(rows * 0.2), width: Math.floor(cols * 0.2), height: Math.floor(rows * 0.3), color: '#27AE60' },
                { name: 'Meeting Area', x: Math.floor(cols * 0.3), y: Math.floor(rows * 0.6), width: Math.floor(cols * 0.3), height: Math.floor(rows * 0.2), color: '#F39C12' }
            ]
        };
        
        return zones[roomType] || zones.living;
    }
    
    calculatePosition(zone, index, cols, rows) {
        // Calculate position within zone with some variation
        const x = zone.x + Math.floor(zone.width * 0.3) + (index % 3) * 2;
        const y = zone.y + Math.floor(zone.height * 0.3) + Math.floor(index / 3) * 2;
        
        return {
            x: Math.min(x, cols - 2),
            y: Math.min(y, rows - 2),
            gridX: x * 2, // Convert to feet
            gridY: y * 2
        };
    }
    
    calculateRotation(category, zone) {
        // Suggest rotation based on category and zone
        const rotations = {
            sofa: 90,
            chair: 45,
            table: 0,
            bed: 90,
            tv_stand: 0,
            lamp: 0
        };
        
        return rotations[category] || 0;
    }
    
    generateTrafficFlow(cols, rows) {
        const paths = [];
        
        // Main pathways
        paths.push({
            type: 'main',
            points: [
                { x: 0, y: Math.floor(rows / 2) },
                { x: cols - 1, y: Math.floor(rows / 2) }
            ]
        });
        
        paths.push({
            type: 'main',
            points: [
                { x: Math.floor(cols / 2), y: 0 },
                { x: Math.floor(cols / 2), y: rows - 1 }
            ]
        });
        
        // Secondary pathways
        for (let i = 1; i < 4; i++) {
            paths.push({
                type: 'secondary',
                points: [
                    { x: Math.floor(cols * i / 4), y: 0 },
                    { x: Math.floor(cols * i / 4), y: rows - 1 }
                ]
            });
        }
        
        return paths;
    }
    
    generateShoppingList(furniture, budget) {
        const budgetMultipliers = {
            economy: 0.7,
            moderate: 1.0,
            premium: 1.5,
            luxury: 2.0
        };
        
        const multiplier = budgetMultipliers[budget] || 1.0;
        
        return furniture.map(item => ({
            ...item,
            price: Math.round(item.price * multiplier),
            link: '#',
            availability: 'In Stock',
            shipping: item.price > 500 ? 'Free' : '$49',
            returnPolicy: '30-day return'
        }));
    }
    
    calculateEstimatedCost(shopping) {
        const subtotal = shopping.reduce((sum, item) => sum + item.price, 0);
        const tax = subtotal * 0.08;
        const shipping = shopping.some(item => item.price < 500) ? 49 : 0;
        const total = subtotal + tax + shipping;
        
        return {
            subtotal: subtotal,
            tax: tax,
            shipping: shipping,
            total: total,
            monthlyPayment: Math.round(total / 12),
            breakdown: shopping.map(item => ({
                name: item.name,
                price: item.price
            }))
        };
    }
    
    generateStyleMatches(roomType, preferredStyle) {
        const styles = [
            { name: 'Modern', match: 95, description: 'Clean lines, minimal ornamentation, functional furniture' },
            { name: 'Minimalist', match: 88, description: 'Less is more, neutral colors, simple forms' },
            { name: 'Scandinavian', match: 82, description: 'Light wood, cozy textures, simple elegance' },
            { name: 'Industrial', match: 76, description: 'Raw materials, exposed elements, urban feel' },
            { name: 'Bohemian', match: 71, description: 'Rich patterns, eclectic mix, plants and textures' },
            { name: 'Traditional', match: 65, description: 'Classic details, rich colors, elegant furniture' },
            { name: 'Contemporary', match: 79, description: 'Current trends, curved lines, bold colors' },
            { name: 'Mid-Century', match: 73, description: 'Retro feel, organic shapes, tapered legs' }
        ];
        
        // Sort by match percentage
        return styles.sort((a, b) => b.match - a.match);
    }
    
    // UI Methods
    showLoading() {
        const loadingEl = document.getElementById('loadingState');
        if (loadingEl) {
            loadingEl.style.display = 'block';
        }
        
        const formEl = document.querySelector('.preference-form');
        if (formEl) {
            formEl.style.display = 'none';
        }
    }
    
    hideLoading() {
        const loadingEl = document.getElementById('loadingState');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }
    
    showError(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'error-message';
        errorEl.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;
        
        document.querySelector('.recommendations-page').prepend(errorEl);
        
        // Show form again
        const formEl = document.querySelector('.preference-form');
        if (formEl) {
            formEl.style.display = 'block';
        }
    }
    
    displayRecommendations(recommendations) {
        const resultsEl = document.getElementById('results');
        if (!resultsEl) return;
        
        resultsEl.style.display = 'block';
        
        // Display color palette
        this.displayColorPalette(recommendations.colorPalette);
        
        // Display furniture layout
        // Pass furniture list as second argument!
        this.displayFurnitureLayout(recommendations.layout, recommendations.furniture); 
        
        // Display shopping list
        this.displayShoppingList(recommendations.shopping);
        
        // Display cost breakdown
        this.displayCostBreakdown(recommendations.estimatedCost);
        
        // Display style matches
        this.displayStyleMatches(recommendations.styleMatches);
        
        // Scroll to results
        resultsEl.scrollIntoView({ behavior: 'smooth' });
    }
    
    displayColorPalette(colors) {
        const paletteEl = document.getElementById('colorPalette');
        if (!paletteEl) return;
        
        paletteEl.innerHTML = colors.map(color => `
            <div class="color-item" style="background: ${color};">
                <span class="color-code">${color}</span>
                <button class="copy-color" onclick="copyToClipboard('${color}')">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        `).join('');
    }
    
    displayFurnitureLayout(layout, furnitureList) {
        const layoutEl = document.getElementById('furnitureList');
        const canvas = document.getElementById('layoutCanvas');
        
        if (canvas && layout) {
            this.drawLayoutOnCanvas(canvas, layout);
        }
        
        if (!layoutEl) return;
        
        let html = '<h3>Recommended Furniture</h3>';
        
        // If we have the full furniture list, display it
        if (furnitureList && Array.isArray(furnitureList)) {
            html += '<div class="furniture-list-items">';
            furnitureList.forEach(item => {
                html += `
                    <div class="furniture-item">
                        <div class="item-details">
                            <h4>${item.name}</h4>
                            <p>Dimensions: ${item.dimensions}</p>
                            <p class="price">$${item.price}</p>
                        </div>
                        <button class="btn-add-small" onclick="window.designRecommender.addToCart(${item.id}, '${item.name.replace(/'/g, "\\'")}')" title="Add to Saved Items">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            // Fallback to layout textual description if list not available
            html += '<div class="layout-visualization">';
            // ... (existing layout zones code) ...
        }
        
        layoutEl.innerHTML = html;
    }
    

    drawLayoutOnCanvas(canvas, layout) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width = canvas.parentElement.clientWidth;
        const height = canvas.height = canvas.parentElement.clientHeight;
        
        // Clear canvas
        ctx.fillStyle = '#112240';
        ctx.fillRect(0, 0, width, height);
        
        // Scale factor: canvas pixels per foot
        const roomWidthFt = layout.grid.cols * layout.grid.cellSize;
        const roomLenFt = layout.grid.rows * layout.grid.cellSize;
        const scaleX = (width - 40) / roomWidthFt; // 20px padding
        const scaleY = (height - 40) / roomLenFt;
        const scale = Math.min(scaleX, scaleY);
        
        const offsetX = (width - roomWidthFt * scale) / 2;
        const offsetY = (height - roomLenFt * scale) / 2;
        
        // Draw Grid
        ctx.strokeStyle = '#233554';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= layout.grid.cols; i++) {
            const x = offsetX + i * layout.grid.cellSize * scale;
            ctx.beginPath();
            ctx.moveTo(x, offsetY);
            ctx.lineTo(x, offsetY + roomLenFt * scale);
            ctx.stroke();
        }
        for (let j = 0; j <= layout.grid.rows; j++) {
            const y = offsetY + j * layout.grid.cellSize * scale;
            ctx.beginPath();
            ctx.moveTo(offsetX, y);
            ctx.lineTo(offsetX + roomWidthFt * scale, y);
            ctx.stroke();
        }
        
        // Draw Zones
        layout.zones.forEach(zone => {
            const x = offsetX + zone.x * layout.grid.cellSize * scale;
            const y = offsetY + zone.y * layout.grid.cellSize * scale;
            const w = zone.width * layout.grid.cellSize * scale;
            const h = zone.height * layout.grid.cellSize * scale;
            
            ctx.fillStyle = zone.color + '33'; // 20% opacity
            ctx.fillRect(x, y, w, h);
            
            ctx.strokeStyle = zone.color;
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, w, h);
            
            ctx.fillStyle = zone.color;
            ctx.font = '12px Poppins';
            ctx.fillText(zone.name, x + 5, y + 15);
        });

        // Draw Furniture Placements
        layout.placements.forEach(placement => {
            const x = offsetX + placement.position.gridX * scale;
            const y = offsetY + placement.position.gridY * scale;
            // Parse dimensions properly (e.g. 84" x 38") or use generic size
            let wFt = 3, hFt = 2; // Default
            if (placement.dimensions) {
                // Try parse dimensions "84" x 38""
                const parts = placement.dimensions.match(/(\d+)"/g);
                if (parts && parts.length >= 2) {
                    wFt = parseInt(parts[0]) / 12;
                    hFt = parseInt(parts[1]) / 12;
                }
            }
            
            const w = wFt * scale;
            const h = hFt * scale;
            
            ctx.fillStyle = '#64FFDA';
            ctx.fillRect(x, y, w, h);
            
            ctx.fillStyle = '#0A192F';
            ctx.font = 'bold 10px Poppins';
            // Truncate name
            const name = placement.item.length > 10 ? placement.item.substring(0, 8) + '...' : placement.item;
            ctx.fillText(name, x + 2, y + h/2 + 3);
        });
    }
    
    displayShoppingList(shopping) {
        const gridEl = document.getElementById('shoppingGrid');
        if (!gridEl) return;
        
        gridEl.innerHTML = shopping.map(item => `
            <div class="shopping-card" data-id="${item.id}">
                <div class="card-image">
                    <img src="${item.image}" alt="${item.name}" onerror="this.src='/static/images/placeholder.jpg'">
                    <span class="card-badge">${item.availability}</span>
                </div>
                <div class="card-content">
                    <h4>${item.name}</h4>
                    <div class="rating">
                        ${this.generateStars(item.rating)}
                        <span>(${item.rating})</span>
                    </div>
                    <p class="price">$${item.price}</p>
                    <p class="store"><i class="fas fa-store"></i> ${item.store}</p>
                    <div class="card-actions">
                        <button class="btn-primary btn-small" onclick="window.designRecommender.addToCart(${item.id}, '${item.name.replace(/'/g, "\\'")}')">
                            <i class="fas fa-shopping-cart"></i> Add to Cart
                        </button>
                        <a href="/ar-viewer?model=${item.id}" class="btn-secondary btn-small">
                            <i class="fas fa-cube"></i> View in AR
                        </a>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    generateStars(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= Math.floor(rating)) {
                stars += '<i class="fas fa-star"></i>';
            } else if (i - 0.5 <= rating) {
                stars += '<i class="fas fa-star-half-alt"></i>';
            } else {
                stars += '<i class="far fa-star"></i>';
            }
        }
        return stars;
    }
    
    displayCostBreakdown(cost) {
        const costEl = document.getElementById('costBreakdown');
        if (!costEl) return;
        
        costEl.innerHTML = `
            <div class="cost-summary">
                <h3>Estimated Cost</h3>
                <div class="cost-item">
                    <span>Subtotal:</span>
                    <span>$${cost.subtotal}</span>
                </div>
                <div class="cost-item">
                    <span>Tax (8%):</span>
                    <span>$${cost.tax.toFixed(2)}</span>
                </div>
                <div class="cost-item">
                    <span>Shipping:</span>
                    <span>$${cost.shipping}</span>
                </div>
                <div class="cost-item total">
                    <span>Total:</span>
                    <span>$${cost.total.toFixed(2)}</span>
                </div>
                <div class="cost-item monthly">
                    <span>Monthly (12 months):</span>
                    <span>$${cost.monthlyPayment}</span>
                </div>
            </div>
        `;
    }
    
    displayStyleMatches(styles) {
        const stylesEl = document.getElementById('styleMatches');
        if (!stylesEl) return;
        
        stylesEl.innerHTML = styles.map(style => `
            <div class="style-match-card">
                <div class="style-header">
                    <h4>${style.name}</h4>
                    <span class="match-percentage">${style.match}%</span>
                </div>
                <p>${style.description}</p>
                <div class="match-bar">
                    <div class="match-progress" style="width: ${style.match}%"></div>
                </div>
                <button class="btn-outline btn-small" onclick="exploreStyle('${style.name}')">
                    Explore ${style.name} Style
                </button>
            </div>
        `).join('');
    }
    
    async saveCurrentDesign() {
        if (!this.recommendations) {
            this.showError('No design to save');
            return;
        }
        
        try {
            const canvas = document.getElementById('layoutCanvas');
            const imageData = canvas ? canvas.toDataURL('image/png') : null;
            
            const response = await fetch('/api/save-design', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    room_type: this.preferences.room_type || 'living',
                    style: this.preferences.style || 'modern',
                    dimensions: {
                        width: this.preferences.width || 12,
                        length: this.preferences.length || 14
                    },
                    elements: this.recommendations, // Store full recommendation object
                    image_data: imageData, // Send the canvas capture
                    ar_model_path: null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Design saved successfully!', 'success');
                // Optionally redirect to dashboard
                setTimeout(() => window.location.href = '/dashboard', 1500);
            } else {
                this.showError('Failed to save design');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showError('Failed to save design');
        }
    }
    
    loadSavedDesigns() {
        const saved = localStorage.getItem('savedDesigns');
        if (saved) {
            try {
                this.savedDesigns = JSON.parse(saved);
            } catch (e) {
                this.savedDesigns = [];
            }
        }
    }
    
    addToCart(itemId, itemName) {
        // Here we would typically make an API call to add the item to the user's saved items or cart
        // For now, let's simulate it and show a success message
        console.log(`Adding item ${itemId}: ${itemName} to cart`);
        
        // Enhance the simulation
        const cartCount = document.querySelector('.cart-count'); // If exists
        if (cartCount) {
            cartCount.textContent = parseInt(cartCount.textContent || '0') + 1;
        }
        
        this.showNotification(`${itemName} added to your saved items!`, 'success');
        
        // Optional: Persist to backend if API exists
        // fetch('/api/save-item', { ... })
    }

    saveToLocalStorage() {
        localStorage.setItem('savedDesigns', JSON.stringify(this.savedDesigns));
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    selectStyle(style) {
        console.log('Selected style:', style);
        // Update UI to show selected style
        document.querySelectorAll('.style-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        document.querySelector(`[data-style="${style}"]`).classList.add('selected');
    }
    
    selectColor(color) {
        console.log('Selected color:', color);
        // Update UI to show selected color
        document.querySelectorAll('.color-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        document.querySelector(`[data-color="${color}"]`).classList.add('selected');
    }
}

// Initialize recommender when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.designRecommender = new DesignRecommender();
});

// Global helper functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        window.designRecommender.showNotification('Color copied to clipboard!', 'success');
    });
}

function addToCart(itemId) {
    console.log('Adding item to cart:', itemId);
    window.designRecommender.showNotification('Item added to cart!', 'success');
}

function viewInAR(itemId) {
    window.location.href = `/ar-viewer?item=${itemId}`;
}

function exploreStyle(styleName) {
    window.location.href = `/design-recommendations?style=${styleName.toLowerCase()}`;
}

function saveDesign() {
    if (window.designRecommender) {
        window.designRecommender.saveCurrentDesign();
    }
}