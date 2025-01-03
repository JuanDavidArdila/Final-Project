## App Initialization

### To start the program, perform the following steps:

1. Navigate to the folder where your project is saved by typing in the terminal:  
   ```bash
   cd "path-to-folder"
   ```

2. Initialize the `main.py` file to start the Flask server by typing:  
   ```bash
   python main.py
   ```

3. Open the `index.html` file using the **"Open with Live Server"** option in the Explorer tab. To do this, right-click the file and select the option.

4. Once the HTML code opens in your default browser, it is recommended to open the **Developer Tools** console using the shortcut `Ctrl+Shift+I`. This console provides updates on the state of the running code.

---

## App Structure

This app is comprised of six main files:

1. **`backend\config.py`**  
   Configures the Flask app. Flask provides the framework for creating the database and APIs.

2. **`frontend\index.html`**  
   The main structure of the frontend, including buttons, sidebars, and containers.

3. **`frontend\index.js`**  
   Contains all map settings and functions for sending and retrieving data from the database.

4. **`backend\functions.py`**  
   Contains thermal and distance functions required for calculations.

5. **`backend\models.py`**  
   Provides schemas for storing raw and transformed data. It facilitates communication between functions and the database.

6. **`backend\main.py`**  
   Creates the database instance and contains all API calls. This is the most important file for the app's functionality.

### Additional Files

1. **`frontend\Icons`**  
   Contains the icons displayed on the map.

2. **`.vscode\settings.json`**  
   Configures the live server port.

---

## Required Libraries and Extensions

### Extensions for VSCode:

- **PyLance**  
- **Python**  
- **Python Debugger**  
- **Prettier - Code Formatter**  

### Libraries Required for the App:

```plaintext
CoolProp          6.6.0
Flask             3.0.3
Flask-Cors        4.0.0
Flask-SQLAlchemy  3.1.1
geopy             2.4.1
```

