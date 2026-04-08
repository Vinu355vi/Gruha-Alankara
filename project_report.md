# Project Report: Gruha Alankara - AI Interior Design

## 1. Abstract
**Gruha Alankara** is an innovative web-based application designed to democratize interior design through the power of Artificial Intelligence (AI) and Augmented Reality (AR). Traditional interior design services can be expensive and time-consuming. Gruha Alankara bridges this gap by allowing users to simply upload a photo of their room to receive instant, personalized design recommendations. The system analyzes the room's dimensions, lighting, and existing elements using computer vision technology and suggests optimal furniture layouts, color palettes, and decor styles. Furthermore, an integrated AR viewer enables users to visualize how recommended furniture pieces would look in their actual space before making a purchase, ensuring confident decision-making.

## 2. Technology Stack
The project is built using a robust and modern technology stack:

*   **Frontend**:
    *   **HTML5 & CSS3**: For structure and styling (Responsive design).
    *   **JavaScript (ES6+)**: For client-side logic and interactivity.
    *   **Three.js**: For rendering 3D graphics and powering the Augmented Reality (AR) experience.
*   **Backend**:
    *   **Python**: The core programming language for server-side logic.
    *   **Flask**: A lightweight WSGI web application framework for handling routes and requests.
    *   **Jinja2**: Templating engine for rendering dynamic HTML pages.
*   **Database**:
    *   **SQLAlchemy**: An Object Relational Mapper (ORM) for managing database interactions (likely SQLite for development).
*   **AI & Computer Vision**:
    *   **OpenCV (cv2)**: For image processing tasks such as edge detection, color extraction, and dimension estimation.
    *   **scikit-learn**: For implementing machine learning algorithms (RandomForestRegressor) to generate personalized design recommendations.
    *   **NumPy**: For numerical operations and data handling.
*   **Authentication**:
    *   **Flask-Login**: For managing user sessions, login, and registration.

## 3. How it Works
The application workflow is designed to be intuitive and user-friendly:

1.  **User Onboarding**: Users register or log in to the platform to access personalized features and save their designs.
2.  **Room Analysis**:
    *   The user uploads an image of their room or captures one using their device's camera.
    *   The **Room Analyzer** module processes this image. It detects key features like walls, floors, and existing furniture.
    *   It estimates room dimensions (width, height, length) and analyzes lighting conditions (natural vs. artificial).
    *   It extracts the dominant color palette of the room.
3.  **AI Recommendations**:
    *   Based on the analysis data and user preferences (e.g., preferred style like "Modern" or "Bohemian", budget range), the **AI Engine** runs recommendation algorithms.
    *   It suggests a complementary **Color Palette** ensuring visual harmony.
    *   It recommends specific **Furniture Items** (sofas, tables, lamps) that fit the room's dimensions and style.
    *   It provides an **Optimal Layout** plan for arranging the furniture.
4.  **Augmented Reality (AR) Visualization**:
    *   The user can select a recommended furniture item.
    *   Using the AR Viewer, the application overlays a 3D model of the furniture onto the live camera feed of the user's room.
    *   Users can rotate, scale, and move the virtual furniture to see exactly how it fits.
5.  **Shopping & Saving**:
    *   The application lists the recommended items with details like price (in INR) and dimensions.
    *   Users can save their generated designs to their dashboard for future reference.

## 4. Architecture
The project follows the **Model-View-Controller (MVC)** architectural pattern:

*   **Model**: Represents the data and business logic.
    *   Defined in `models/` and `app.py`.
    *   Includes entities like `User`, `Design`, `SavedItem`, and `UserPreference`.
    *   Interacts with the database via SQLAlchemy.
*   **View**: Represents the user interface.
    *   Defined in `templates/` (HTML files).
    *   Displays data provided by the controller and captures user input.
    *   Includes `index.html`, `dashboard.html`, `ar-viewer.html`, `room-analysis.html`, etc.
*   **Controller**: Manages the flow of data.
    *   Defined in `app.py` (Route handlers).
    *   Receives user requests (e.g., URL access, form submissions).
    *   Calls utility modules (`utils/`) to process data (Analysis, AI).
    *   Updates the Model and renders the appropriate View.

## 5. Structure
The project is organized into a modular directory structure:

```
gruha-alankara/
├── app.py                      # Main application entry point and route definitions
├── config.py                   # Configuration settings (Secret keys, DB URI)
├── requirements.txt            # List of Python dependencies
├── run.py                      # Script to run the Flask development server
├── models/                     # Database models
│   ├── design_model.py         # Models related to stored designs
│   └── recommendation_model.py # Models for recommendation logic
├── static/                     # Static assets
│   ├── css/                    # Stylesheets (style.css, shopping-style.css, etc.)
│   ├── images/                 # Image assets (icons, furniture images, etc.)
│   └── js/                     # JavaScript files (ar-viewer.js, three-ar.js, etc.)
├── templates/                  # HTML Templates
│   ├── base.html               # Base template with common layout (nav, footer)
│   ├── index.html              # Landing page
│   ├── login.html              # Login page
│   ├── dashboard.html          # User dashboard
│   ├── room-analysis.html      # Room analysis interface
│   ├── design-recommendations.html # Results page
│   └── ar-viewer.html          # AR utilization page
└── utils/                      # Utility modules (Business Logic)
    ├── room_analyzer.py        # Computer vision logic for image analysis
    ├── ai_recommendations.py   # Machine learning logic for suggestions
    └── ar_helper.py            # Helper functions for AR operations
```

## 6. Functions/Modules
*   **`RoomAnalyzer` (`utils/room_analyzer.py`)**:
    *   `analyze_image(image_path)`: Orchestrates the full analysis pipeline.
    *   `estimate_dimensions(image)`: Uses perspective geometry to guess room size.
    *   `detect_walls(image)`: Identifies vertical planes representing walls.
    *   `extract_colors(image)`: Uses clustering to find dominant colors.
*   **`AIRecommendations` (`utils/ai_recommendations.py`)**:
    *   `get_style_recommendations(...)`: Returns ranked design styles.
    *   `_calculate_style_score(...)`: Internal logic to score how well a style fits a room.
*   **`ARHelper` (`utils/ar_helper.py`)**:
    *   Manages 3D model paths and compatibility checks for the frontend AR viewer.
*   **Routes (`app.py`)**:
    *   `/analyze-room`: Endpoint to handle image uploads and return analysis JSON.
    *   `/recommendations`: Endpoint to generate and return design suggestions.

## 7. Viva Questions

**Q1: What algorithm is used for the AI recommendations?**
**A:** We utilize a **Random Forest Regressor** from the scikit-learn library. It is an ensemble learning method that constructs multiple decision trees during training and outputs the mean prediction of the individual trees, providing robust recommendations for styles and colors.

**Q2: How does the Room/Image Analysis work?**
**A:** It uses **OpenCV**. The system loads the image and converts it to RGB. It then applies techniques like edge detection (Canny) and Hough Line Transform to detect straight lines (walls/floor boundaries) and color clustering (K-Means) to extract the dominant color palette.

**Q3: How is the Augmented Reality (AR) implemented?**
**A:** The AR functionality is client-side, built using **JavaScript** and libraries like **Three.js**. It accesses the device's camera stream via the browser's `navigator.mediaDevices` API and renders 3D models (GLB/GLTF format) onto a canvas layered over the video feed.

**Q4: What is the purpose of Flask in this project?**
**A:** Flask acts as the web server and controller. It routes incoming HTTP requests to the appropriate python functions, manages user sessions (login/logout), interacts with the database to fetch or save designs, and renders the HTML templates to the user's browser.

**Q5: Is the application responsive?**
**A:** Yes, the frontend relies on CSS Grid and Flexbox (as seen in `shopping-style.css`) to ensure the layout adapts to different screen sizes, making it accessible on both desktops and mobile devices.

**Q6: How are user passwords stored?**
**A:** Passwords are **hashed** using `generate_password_hash` from `werkzeug.security` before being stored in the database. This ensures that actual passwords are never exposed, even if the database is compromised.
