// Three.js AR setup for 3D model rendering
class ThreeARViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.models = {};
        this.currentModel = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.clock = new THREE.Clock();
        
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x111122);
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(5, 5, 10);
        this.camera.lookAt(0, 0, 0);
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);
        
        // Add lights
        this.setupLights();
        
        // Add helpers
        this.setupHelpers();
        
        // Add controls
        this.setupControls();
        
        // Add event listeners
        this.setupEventListeners();
        
        // Start animation loop
        this.animate();
    }
    
    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404060);
        this.scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        const d = 15;
        directionalLight.shadow.camera.left = -d;
        directionalLight.shadow.camera.right = d;
        directionalLight.shadow.camera.top = d;
        directionalLight.shadow.camera.bottom = -d;
        directionalLight.shadow.camera.near = 1;
        directionalLight.shadow.camera.far = 50;
        this.scene.add(directionalLight);
        
        // Fill lights
        const fillLight1 = new THREE.PointLight(0x446688, 0.5);
        fillLight1.position.set(-5, 3, 5);
        this.scene.add(fillLight1);
        
        const fillLight2 = new THREE.PointLight(0x884466, 0.3);
        fillLight2.position.set(5, 2, -5);
        this.scene.add(fillLight2);
        
        // Add light helpers for debugging
        // const helper = new THREE.DirectionalLightHelper(directionalLight, 1);
        // this.scene.add(helper);
    }
    
    setupHelpers() {
        // Grid helper
        const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
        this.scene.add(gridHelper);
        
        // Axes helper (optional)
        // const axesHelper = new THREE.AxesHelper(5);
        // this.scene.add(axesHelper);
        
        // Add a simple floor plane for shadows
        const planeGeometry = new THREE.PlaneGeometry(20, 20);
        const planeMaterial = new THREE.ShadowMaterial({ opacity: 0.3, color: 0x000000 });
        const plane = new THREE.Mesh(planeGeometry, planeMaterial);
        plane.rotation.x = -Math.PI / 2;
        plane.position.y = 0;
        plane.receiveShadow = true;
        this.scene.add(plane);
    }
    
    setupControls() {
        // Simple orbit controls implementation
        let isDragging = false;
        let previousMousePosition = { x: 0, y: 0 };
        
        this.container.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = {
                x: e.clientX,
                y: e.clientY
            };
        });
        
        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaMove = {
                x: e.clientX - previousMousePosition.x,
                y: e.clientY - previousMousePosition.y
            };
            
            if (this.currentModel) {
                // Rotate model
                this.currentModel.rotation.y += deltaMove.x * 0.01;
                this.currentModel.rotation.x += deltaMove.y * 0.01;
            } else {
                // Rotate camera around scene
                const radius = Math.sqrt(
                    this.camera.position.x * this.camera.position.x +
                    this.camera.position.z * this.camera.position.z
                );
                
                const angle = Math.atan2(this.camera.position.z, this.camera.position.x);
                const newAngle = angle + deltaMove.x * 0.01;
                
                this.camera.position.x = radius * Math.cos(newAngle);
                this.camera.position.z = radius * Math.sin(newAngle);
                this.camera.lookAt(0, 1, 0);
            }
            
            previousMousePosition = {
                x: e.clientX,
                y: e.clientY
            };
        });
        
        window.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        // Zoom with scroll
        this.container.addEventListener('wheel', (e) => {
            e.preventDefault();
            
            const delta = e.deltaY * 0.01;
            const direction = new THREE.Vector3();
            this.camera.getWorldDirection(direction);
            
            this.camera.position.addScaledVector(direction, delta);
            
            // Limit zoom distance
            const distance = this.camera.position.length();
            if (distance < 3) {
                this.camera.position.normalize().multiplyScalar(3);
            } else if (distance > 20) {
                this.camera.position.normalize().multiplyScalar(20);
            }
        });
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Raycaster for object picking
        this.container.addEventListener('click', (e) => {
            this.mouse.x = (e.clientX / this.renderer.domElement.clientWidth) * 2 - 1;
            this.mouse.y = -(e.clientY / this.renderer.domElement.clientHeight) * 2 + 1;
            
            this.raycaster.setFromCamera(this.mouse, this.camera);
            
            const intersects = this.raycaster.intersectObjects(this.scene.children);
            
            if (intersects.length > 0) {
                const clickedObject = intersects[0].object;
                if (clickedObject.userData.clickable) {
                    this.onObjectClick(clickedObject);
                }
            }
        });
    }
    
    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    loadModel(modelName, modelPath, callback) {
        // In production, use GLTFLoader
        // This is a simplified example using primitive geometries
        
        let geometry;
        let material;
        
        switch(modelName) {
            case 'sofa':
                geometry = new THREE.BoxGeometry(2, 1, 1);
                material = new THREE.MeshStandardMaterial({ color: 0x44aa88 });
                break;
            case 'table':
                geometry = new THREE.CylinderGeometry(0.8, 0.8, 0.1, 32);
                material = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
                break;
            case 'chair':
                geometry = new THREE.BoxGeometry(0.6, 0.8, 0.6);
                material = new THREE.MeshStandardMaterial({ color: 0xCCCCCC });
                break;
            case 'lamp':
                geometry = new THREE.ConeGeometry(0.3, 1.5, 32);
                material = new THREE.MeshStandardMaterial({ color: 0xFFD700 });
                break;
            default:
                geometry = new THREE.SphereGeometry(0.5, 32);
                material = new THREE.MeshStandardMaterial({ color: 0x44aa88 });
        }
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.position.y = geometry.parameters.height / 2;
        mesh.userData = { 
            name: modelName,
            clickable: true,
            type: 'furniture'
        };
        
        this.models[modelName] = mesh;
        
        if (callback) callback(mesh);
        
        return mesh;
    }
    
    loadGLTFModel(modelName, modelPath, callback) {
        // Using GLTFLoader for more complex models
        const loader = new THREE.GLTFLoader();
        
        loader.load(
            modelPath,
            (gltf) => {
                const model = gltf.scene;
                model.traverse((node) => {
                    if (node.isMesh) {
                        node.castShadow = true;
                        node.receiveShadow = true;
                    }
                });
                
                model.userData = {
                    name: modelName,
                    clickable: true,
                    type: 'furniture'
                };
                
                this.models[modelName] = model;
                
                if (callback) callback(model);
            },
            (xhr) => {
                console.log(`${modelName} ${(xhr.loaded / xhr.total * 100)}% loaded`);
            },
            (error) => {
                console.error('Error loading model:', error);
            }
        );
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
    
    placeModel(position = { x: 0, y: 0, z: 0 }, rotation = { x: 0, y: 0, z: 0 }, scale = 1) {
        if (!this.currentModel) return;
        
        this.currentModel.position.set(position.x, position.y, position.z);
        this.currentModel.rotation.set(rotation.x, rotation.y, rotation.z);
        this.currentModel.scale.set(scale, scale, scale);
    }
    
    removeModel() {
        if (this.currentModel) {
            this.scene.remove(this.currentModel);
            this.currentModel = null;
        }
    }
    
    onObjectClick(object) {
        console.log('Clicked on:', object.userData.name);
        
        // Highlight clicked object
        if (object.material) {
            if (Array.isArray(object.material)) {
                object.material.forEach(mat => {
                    mat.emissive = new THREE.Color(0x333333);
                });
            } else {
                object.material.emissive = new THREE.Color(0x333333);
            }
            
            setTimeout(() => {
                if (Array.isArray(object.material)) {
                    object.material.forEach(mat => {
                        mat.emissive = new THREE.Color(0x000000);
                    });
                } else {
                    object.material.emissive = new THREE.Color(0x000000);
                }
            }, 200);
        }
        
        // Dispatch custom event
        const event = new CustomEvent('objectClicked', {
            detail: { object: object.userData }
        });
        this.container.dispatchEvent(event);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const delta = this.clock.getDelta();
        
        // Animate current model if exists
        if (this.currentModel && this.currentModel.userData.animate !== false) {
            // Subtle floating animation
            this.currentModel.position.y = 0.5 + Math.sin(Date.now() * 0.003) * 0.05;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    captureScreenshot() {
        this.renderer.render(this.scene, this.camera);
        const dataURL = this.renderer.domElement.toDataURL('image/png');
        
        const link = document.createElement('a');
        link.download = 'ar-capture.png';
        link.href = dataURL;
        link.click();
    }
    
    exportScene() {
        const sceneData = {
            models: Object.keys(this.models).map(key => ({
                name: key,
                position: this.models[key].position,
                rotation: this.models[key].rotation,
                scale: this.models[key].scale
            })),
            camera: {
                position: this.camera.position,
                target: [0, 1, 0]
            }
        };
        
        return JSON.stringify(sceneData, null, 2);
    }
    
    loadScene(sceneData) {
        try {
            const data = typeof sceneData === 'string' ? JSON.parse(sceneData) : sceneData;
            
            // Clear existing models
            this.scene.children = this.scene.children.filter(child => 
                child.type === 'GridHelper' || 
                child.type === 'AmbientLight' || 
                child.type === 'DirectionalLight' ||
                child.type === 'PointLight'
            );
            
            // Load models from data
            data.models.forEach(modelInfo => {
                if (this.models[modelInfo.name]) {
                    const model = this.models[modelInfo.name];
                    model.position.copy(modelInfo.position);
                    model.rotation.copy(modelInfo.rotation);
                    model.scale.copy(modelInfo.scale);
                    this.scene.add(model);
                }
            });
            
            // Restore camera
            this.camera.position.copy(data.camera.position);
            this.camera.lookAt(data.camera.target[0], data.camera.target[1], data.camera.target[2]);
            
        } catch (error) {
            console.error('Error loading scene:', error);
        }
    }
}

// Initialize ThreeARViewer when needed
window.ThreeARViewer = ThreeARViewer;