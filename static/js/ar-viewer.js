// AR Viewer JavaScript
class ARViewer {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.models = []; // Array to hold multiple models
        this.currentModel = null;
        this.isInitialized = false;
        
        // Raycaster for object selection and movement
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.isDragging = false;
        
        // Event binding
        this.onMouseDown = this.onMouseDown.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        this.onTouchStart = this.onTouchStart.bind(this);
        this.onTouchMove = this.onTouchMove.bind(this);
        this.onTouchEnd = this.onTouchEnd.bind(this);
        
        document.addEventListener('mousedown', this.onMouseDown);
        document.addEventListener('mousemove', this.onMouseMove);
        document.addEventListener('mouseup', this.onMouseUp);
        document.addEventListener('touchstart', this.onTouchStart, { passive: false });
        document.addEventListener('touchmove', this.onTouchMove, { passive: false });
        document.addEventListener('touchend', this.onTouchEnd);
    }
    
    updateMousePosition(clientX, clientY) {
        const canvas = this.renderer.domElement;
        const rect = canvas.getBoundingClientRect();
        this.mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;
    }

    onMouseDown(event) {
        if (!this.isInitialized) return;
        this.updateMousePosition(event.clientX, event.clientY);
        this.checkIntersection();
        if (this.currentModel) this.isDragging = true;
    }
    
    onMouseMove(event) {
        if (!this.isInitialized) return;
        this.updateMousePosition(event.clientX, event.clientY);
        if (this.isDragging) this.dragModel();
    }
    
    onMouseUp(event) {
        this.isDragging = false;
    }

    onTouchStart(event) {
        if (!this.isInitialized || event.touches.length === 0) return;
        // event.preventDefault(); // Prevent scrolling while interacting
        const touch = event.touches[0];
        this.updateMousePosition(touch.clientX, touch.clientY);
        this.checkIntersection();
        if (this.currentModel) this.isDragging = true;
    }
    
    onTouchMove(event) {
        if (!this.isInitialized || event.touches.length === 0) return;
        if (this.isDragging) event.preventDefault(); // Only prevent scroll if dragging
        const touch = event.touches[0];
        this.updateMousePosition(touch.clientX, touch.clientY);
        if (this.isDragging) this.dragModel();
    }
    
    onTouchEnd(event) {
        this.isDragging = false;
    }
    
    checkIntersection() {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Intersect with models
        const intersects = this.raycaster.intersectObjects(this.models, true);
        
        if (intersects.length > 0) {
            // Find the top-level group
            let object = intersects[0].object;
            while (object.parent && object.parent !== this.scene) {
                object = object.parent;
            }
            
            this.currentModel = object;
            // Optional: Visual feedback
        }
    }
    
    dragModel() {
        if (!this.currentModel || !this.floorPlane) return;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObject(this.floorPlane);
        
        if (intersects.length > 0) {
            const point = intersects[0].point;
            this.currentModel.position.x = point.x;
            this.currentModel.position.z = point.z;
        }
    }
    
    init() {
        if (this.isInitialized) return;
        
        // Initialize Three.js scene
        this.scene = new THREE.Scene();
        // Remove solid background to allow video to show through
        // this.scene.background = new THREE.Color(0x111122);
        
        // Initialize camera
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 3, 5); // Raised camera slightly
        this.camera.lookAt(0, 0, 0);
        
        // Initialize renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); // alpha: true is crucial for AR
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x000000, 0); // Transparent clear color
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Append renderer canvas to container
        const container = document.getElementById('arCanvas');
        if (container) {
            this.renderer.domElement.style.position = 'absolute';
            this.renderer.domElement.style.top = '0';
            this.renderer.domElement.style.left = '0';
            this.renderer.domElement.style.zIndex = '1';
            container.appendChild(this.renderer.domElement);
            
            // Add orbit controls-like behavior for "viewing" (if not pure AR)
            // But since this is AR, we usually move the camera.
            // If the user wants to "adjust" the object (move/rotate), we use the UI buttons.
        }
        
        // Setup Video Background
        this.setupVideoBackground();

        // Add lights
        this.addLights();
        
        // Add grid helper (optional in AR, but good for reference)
        const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
        gridHelper.position.y = 0; // Floor level
        this.scene.add(gridHelper);
        
        // Add shadow catching plane
        const shadowGeometry = new THREE.PlaneGeometry(20, 20);
        const shadowMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });
        const shadowPlane = new THREE.Mesh(shadowGeometry, shadowMaterial);
        shadowPlane.rotation.x = -Math.PI / 2;
        shadowPlane.position.y = 0; // Same level as grid
        shadowPlane.receiveShadow = true;
        this.floorPlane = shadowPlane; // Used for dragging
        this.scene.add(shadowPlane);
        
        this.isInitialized = true;
        
        // Start animation loop
        this.animate();
    }

    setupVideoBackground() {
        const video = document.createElement('video');
        video.id = 'ar-video-background';
        video.autoplay = true;
        video.muted = true;
        video.playsInline = true;
        video.style.position = 'absolute';
        video.style.top = '0';
        video.style.left = '0';
        video.style.width = '100%';
        video.style.height = '100%';
        video.style.objectFit = 'cover';
        video.style.zIndex = '-1'; // Behind the canvas
        
        const container = document.getElementById('arCanvas');
        if (container) {
            container.insertBefore(video, container.firstChild);
        }

        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            const constraints = { 
                video: { 
                    facingMode: 'environment' // Prefer back camera on mobile
                } 
            };

            navigator.mediaDevices.getUserMedia(constraints)
                .then(function(stream) {
                    video.srcObject = stream;
                    video.play();
                })
                .catch(function(error) {
                    console.error("Unable to access the camera/webcam.", error);
                    alert("Could not access the camera. Please ensure you have given permission.");
                });
        } else {
            console.warn('MediaDevices interface not available.');
        }
    }
    
    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404060);
        this.scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        const d = 10;
        directionalLight.shadow.camera.left = -d;
        directionalLight.shadow.camera.right = d;
        directionalLight.shadow.camera.top = d;
        directionalLight.shadow.camera.bottom = -d;
        directionalLight.shadow.camera.near = 1;
        directionalLight.shadow.camera.far = 15;
        this.scene.add(directionalLight);
        
        // Fill light
        const fillLight = new THREE.PointLight(0x446688, 0.5);
        fillLight.position.set(-5, 3, 5);
        this.scene.add(fillLight);
        
        // Back light
        const backLight = new THREE.PointLight(0x884466, 0.3);
        backLight.position.set(0, 2, -5);
        this.scene.add(backLight);
    }
    
    loadModel(modelName, modelPath) {
        // Create specific 3D model based on selection
        let mesh;
        
        switch(modelName) {
            case 'modern_sofa':
                mesh = this.createModernSofa();
                break;
            case 'sectional_sofa':
                mesh = this.createSectionalSofa();
                break;
            case 'coffee_table':
                mesh = this.createCoffeeTable();
                break;
            case 'dining_table':
                mesh = this.createDiningTable();
                break;
            case 'armchair':
                mesh = this.createArmchair();
                break;
            case 'dining_chair':
                mesh = this.createDiningChair();
                break;
            default:
                // Fallback geometry
                const geometry = new THREE.BoxGeometry(1, 1, 1);
                const material = new THREE.MeshStandardMaterial({ 
                    color: 0x44aa88,
                    roughness: 0.7,
                    metalness: 0.1
                });
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.y = 0.5;
        }
        
        // Setup shadow casting for all children if it's a group
        if (mesh.isGroup) {
            mesh.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
        } else {
            mesh.castShadow = true;
            mesh.receiveShadow = true;
        }
        
        // Add metadata for identification
        mesh.userData = { 
            name: modelName, 
            id: Date.now(),
            isFurniture: true
        };
        
        // Add to scene
        this.scene.add(mesh);
        
        // Add to models array
        this.models.push(mesh);
        
        // Set as current selected model
        this.currentModel = mesh;
        
        return mesh;
    }

    createModernSofa() {
        const group = new THREE.Group();
        
        // Materials
        const fabricMat = new THREE.MeshStandardMaterial({ 
            color: 0x5D737E, 
            roughness: 0.9,
            metalness: 0.1
        });
        const woodMat = new THREE.MeshStandardMaterial({ 
            color: 0x3E2723, 
            roughness: 0.8 
        });
        
        // Base seat
        const seatGeo = new THREE.BoxGeometry(2.2, 0.4, 0.8);
        const seat = new THREE.Mesh(seatGeo, fabricMat);
        seat.position.y = 0.4;
        group.add(seat);
        
        // Backrest
        const backGeo = new THREE.BoxGeometry(2.2, 0.6, 0.2);
        const back = new THREE.Mesh(backGeo, fabricMat);
        back.position.set(0, 0.9, -0.3);
        group.add(back);
        
        // Armrests
        const armGeo = new THREE.BoxGeometry(0.3, 0.6, 0.8);
        const leftArm = new THREE.Mesh(armGeo, fabricMat);
        leftArm.position.set(-0.95, 0.6, 0);
        group.add(leftArm);
        
        const rightArm = new THREE.Mesh(armGeo, fabricMat);
        rightArm.position.set(0.95, 0.6, 0);
        group.add(rightArm);
        
        // Legs
        const legGeo = new THREE.CylinderGeometry(0.05, 0.04, 0.2, 8);
        const legPositions = [
            [-1, 0.1, 0.3], [1, 0.1, 0.3],
            [-1, 0.1, -0.3], [1, 0.1, -0.3]
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeo, woodMat);
            leg.position.set(...pos);
            group.add(leg);
        });
        
        return group;
    }

    createSectionalSofa() {
        const group = new THREE.Group();
        
        const fabricMat = new THREE.MeshStandardMaterial({ 
            color: 0x90A4AE, 
            roughness: 0.8,
            metalness: 0.05
        });
        const woodMat = new THREE.MeshStandardMaterial({ 
            color: 0x4E342E, 
            roughness: 0.9 
        });
        
        // Main validation
        // Section 1 (Main)
        const s1Seat = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.4, 0.8), fabricMat);
        s1Seat.position.set(0, 0.4, 0);
        group.add(s1Seat);
        
        const s1Back = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.6, 0.2), fabricMat);
        s1Back.position.set(0, 0.9, -0.3);
        group.add(s1Back);
        
        // Section 2 (L-extension perpendicular)
        const s2Seat = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.4, 1.4), fabricMat);
        s2Seat.position.set(1.4, 0.4, 0.3); // Extend to right and forward
        group.add(s2Seat);
        
        const s2Back = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.6, 1.4), fabricMat);
        s2Back.position.set(1.9, 0.9, 0.3); // Back on the right side
        group.add(s2Back);

        // Legs
        const legGeo = new THREE.CylinderGeometry(0.05, 0.04, 0.2, 8);
        const legPositions = [
            [-0.9, 0.1, 0.3], [-0.9, 0.1, -0.3], // Left side
            [0.9, 0.1, -0.3], // Middle back
            [1.7, 0.1, -0.3], // Far right back 
            [1.7, 0.1, 0.9],  // Far right front
            [0.9, 0.1, 0.9]   // Inner corner front
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeo, woodMat);
            leg.position.set(...pos);
            group.add(leg);
        });

        return group;
    }

    createCoffeeTable() {
        const group = new THREE.Group();
        
        const woodMat = new THREE.MeshStandardMaterial({ 
            color: 0x8D6E63, 
            roughness: 0.4,
            metalness: 0.1
        });
        
        // Table top
        const topGeo = new THREE.CylinderGeometry(0.6, 0.6, 0.05, 32);
        const top = new THREE.Mesh(topGeo, woodMat);
        top.position.y = 0.45;
        group.add(top);
        
        // Legs
        const legGeo = new THREE.CylinderGeometry(0.04, 0.03, 0.45, 8);
        const legPositions = [
            [0.3, 0.225, 0.3], [-0.3, 0.225, 0.3],
            [0.3, 0.225, -0.3], [-0.3, 0.225, -0.3]
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeo, woodMat);
            leg.position.set(...pos);
            group.add(leg);
        });
        
        return group;
    }

    createDiningTable() {
        const group = new THREE.Group();
        
        const topMat = new THREE.MeshStandardMaterial({ 
            color: 0xFFFFFF, 
            roughness: 0.1,
            metalness: 0.0
        }); // Marble look
        const legMat = new THREE.MeshStandardMaterial({ 
            color: 0x212121, 
            roughness: 0.5,
            metalness: 0.5 
        });
        
        // Table top
        const topGeo = new THREE.BoxGeometry(1.8, 0.08, 0.9);
        const top = new THREE.Mesh(topGeo, topMat);
        top.position.y = 0.75;
        group.add(top);
        
        // Legs
        const legGeo = new THREE.BoxGeometry(0.08, 0.75, 0.08);
        const legPositions = [
            [-0.8, 0.375, 0.35], [0.8, 0.375, 0.35],
            [-0.8, 0.375, -0.35], [0.8, 0.375, -0.35]
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeo, legMat);
            leg.position.set(...pos);
            group.add(leg);
        });
        
        return group;
    }

    createArmchair() {
        const group = new THREE.Group();
        
        const fabricMat = new THREE.MeshStandardMaterial({ 
            color: 0xFF7043, 
            roughness: 0.9 
        });
        const woodMat = new THREE.MeshStandardMaterial({ 
            color: 0x5D4037, 
            roughness: 0.6 
        });
        
        // Seat
        const seatGeo = new THREE.BoxGeometry(0.7, 0.3, 0.7);
        const seat = new THREE.Mesh(seatGeo, fabricMat);
        seat.position.y = 0.4;
        group.add(seat);
        
        // Back
        const backGeo = new THREE.BoxGeometry(0.7, 0.6, 0.15);
        const back = new THREE.Mesh(backGeo, fabricMat);
        back.position.set(0, 0.85, -0.275);
        group.add(back);
        
        // Arms
        const armGeo = new THREE.BoxGeometry(0.15, 0.4, 0.7);
        const leftArm = new THREE.Mesh(armGeo, fabricMat);
        leftArm.position.set(-0.35, 0.55, 0);
        group.add(leftArm);
        
        const rightArm = new THREE.Mesh(armGeo, fabricMat);
        rightArm.position.set(0.35, 0.55, 0);
        group.add(rightArm);
        
        // Legs
        const legGeo = new THREE.CylinderGeometry(0.04, 0.03, 0.25, 8);
        const legPositions = [
            [-0.3, 0.125, 0.3], [0.3, 0.125, 0.3],
            [-0.3, 0.125, -0.3], [0.3, 0.125, -0.3]
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeo, woodMat);
            leg.position.set(...pos);
            group.add(leg);
        });
        
        return group;
    }

    createDiningChair() {
        const group = new THREE.Group();
        
        const fabricMat = new THREE.MeshStandardMaterial({ 
            color: 0xE0E0E0, 
            roughness: 0.7 
        });
        const woodMat = new THREE.MeshStandardMaterial({ 
            color: 0x8D6E63, 
            roughness: 0.6 
        });
        
        // Seat
        const seatGeo = new THREE.BoxGeometry(0.5, 0.05, 0.5);
        const seat = new THREE.Mesh(seatGeo, fabricMat);
        seat.position.y = 0.45;
        group.add(seat);
        
        // Back
        const backGeo = new THREE.BoxGeometry(0.5, 0.5, 0.05);
        const back = new THREE.Mesh(backGeo, woodMat);
        back.position.set(0, 0.7, -0.225);
        group.add(back);

        // Back Supports
        const supportGeo = new THREE.BoxGeometry(0.04, 0.45, 0.04);
        const leftSup = new THREE.Mesh(supportGeo, woodMat);
        leftSup.position.set(-0.2, 0.225, -0.225);
        group.add(leftSup);
        
        const rightSup = new THREE.Mesh(supportGeo, woodMat);
        rightSup.position.set(0.2, 0.225, -0.225);
        group.add(rightSup);

        // Front Legs
        const legGeo = new THREE.BoxGeometry(0.04, 0.45, 0.04);
        const frontLeft = new THREE.Mesh(legGeo, woodMat);
        frontLeft.position.set(-0.2, 0.225, 0.2);
        group.add(frontLeft);
        
        const frontRight = new THREE.Mesh(legGeo, woodMat);
        frontRight.position.set(0.2, 0.225, 0.2);
        group.add(frontRight);
        
        return group;
    }
    
    setCurrentModel(modelName) {
        if (this.currentModel) {
            this.scene.remove(this.currentModel);
        }
        
        if (this.models[modelName]) {
            this.currentModel = this.models[modelName];
            this.scene.add(this.currentModel);
        }
    }
    
    placeModel(position, rotation, scale) {
        if (!this.currentModel) return;
        
        this.currentModel.position.set(position.x, position.y, position.z);
        this.currentModel.rotation.set(rotation.x, rotation.y, rotation.z);
        this.currentModel.scale.set(scale, scale, scale);
    }
    
    rotateModel(angle, axis = 'y') {
        if (!this.currentModel) return;
        
        switch(axis) {
            case 'x':
                this.currentModel.rotation.x += angle;
                break;
            case 'y':
                this.currentModel.rotation.y += angle;
                break;
            case 'z':
                this.currentModel.rotation.z += angle;
                break;
        }
    }
    
    scaleModel(factor) {
        if (!this.currentModel) return;
        
        this.currentModel.scale.x *= factor;
        this.currentModel.scale.y *= factor;
        this.currentModel.scale.z *= factor;
    }
    
    resetModel() {
        if (!this.currentModel) return;
        
        this.currentModel.position.set(0, 0.5, 0);
        this.currentModel.rotation.set(0, 0, 0);
        this.currentModel.scale.set(1, 1, 1);
    }
    
    removeModel() {
        if (this.currentModel) {
            this.scene.remove(this.currentModel);
            this.currentModel = null;
        }
    }
    
    capture() {
        // Render the scene to a canvas and capture as image
        this.renderer.render(this.scene, this.camera);
        const dataURL = this.renderer.domElement.toDataURL('image/png');
        
        // Create download link
        const link = document.createElement('a');
        link.download = 'ar-capture.png';
        link.href = dataURL;
        link.click();
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.currentModel) {
            // Add subtle floating animation
            this.currentModel.position.y = 0.5 + Math.sin(Date.now() * 0.003) * 0.05;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    resize() {
        if (this.camera && this.renderer) {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        }
    }
}

// Initialize AR Viewer when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.arViewer = new ARViewer();
    
    // Add resize listener
    window.addEventListener('resize', () => {
        if (window.arViewer) {
            window.arViewer.resize();
        }
    });
});