from flask import Flask, render_template,render_template_string, request, redirect, url_for, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong secret key!

# ✅ MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'mydatabase'

# ✅ Initialize MySQL
mysql = MySQL(app)

# ✅ Google OAuth2 setup
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Only for development
google_bp = make_google_blueprint(
    client_id="982380431211-ikqh860nkmdkloup31kih4rbfus2a1og.apps.googleusercontent.com",
    client_secret="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",
    redirect_url="/login/google/authorized",
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")


# ✅ Home page
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/select")
def select():
    return render_template("select.html")
@app.route("/exercise")
def exercise():
    videos = [
        {"emoji": "💪", "title": "Full Body HIIT", "file": "videos/full_body_hiit.mp4", "duration": "30 min", "level": "Intermediate"},
        {"emoji": "🦵", "title": "Lower Body Strength", "file": "videos/lower_body_strength.mp4", "duration": "25 min", "level": "Beginner"},
        {"emoji": "💪", "title": "Upper Body Power", "file": "videos/upper_body_power.mp4", "duration": "35 min", "level": "Advanced"},
        {"emoji": "🧘", "title": "Core & Flexibility", "file": "videos/core_flexibility.mp4", "duration": "20 min", "level": "All Levels"},
        {"emoji": "🏃", "title": "Cardio Blast", "file": "videos/cardio_blast.mp4", "duration": "40 min", "level": "Intermediate"},
        {"emoji": "🧘‍♀️", "title": "Yoga & Stretching", "file": "videos/yoga_stretching.mp4", "duration": "30 min", "level": "All Levels"}
    ]
    return render_template("exercise.html", videos=videos)
@app.route("/meal_plans")

def meal_plans():
    return render_template("meal_plans.html")

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        try:
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', 'male')
            unit_system = request.form.get('unit_system', 'metric')
            
            # Get measurements based on unit system
            if unit_system == 'metric':
                height_cm = float(request.form.get('height_cm', 0))
                weight_kg = float(request.form.get('weight_kg', 0))
            else:
                height_ft = float(request.form.get('height_ft', 0))
                height_in = float(request.form.get('height_in', 0))
                weight_lbs = float(request.form.get('weight_lbs', 0))
                
                # Convert to metric
                height_cm = (height_ft * 12 + height_in) * 2.54
                weight_kg = weight_lbs * 0.453592
            
            # Calculate BMI
            height_m = height_cm / 100
            bmi = weight_kg / (height_m ** 2)
            
            # Determine category
            if bmi < 18.5:
                category = "Underweight"
                category_class = "underweight"
                health_description = "Your BMI indicates you are underweight. This may increase risk of nutritional deficiencies, weakened immune system, and osteoporosis."
                recommendations = [
                    "Consult with a healthcare provider or nutritionist",
                    "Increase caloric intake with nutrient-dense foods",
                    "Include strength training exercises",
                    "Monitor your health regularly"
                ]
            elif bmi < 25:
                category = "Normal Weight"
                category_class = "normal"
                health_description = "Congratulations! Your BMI is in the healthy range. Maintaining this weight reduces your risk of serious health conditions."
                recommendations = [
                    "Maintain a balanced diet with fruits and vegetables",
                    "Stay physically active (150 min/week moderate exercise)",
                    "Get adequate sleep (7-9 hours)",
                    "Stay hydrated and manage stress"
                ]
            elif bmi < 30:
                category = "Overweight"
                category_class = "overweight"
                health_description = "Your BMI indicates you are overweight. This may increase risk of heart disease, type 2 diabetes, and certain cancers."
                recommendations = [
                    "Aim for gradual weight loss (0.5-1 kg per week)",
                    "Reduce portion sizes and processed foods",
                    "Increase physical activity gradually",
                    "Consider consulting a healthcare provider"
                ]
            else:
                category = "Obese"
                category_class = "obese"
                health_description = "Your BMI indicates obesity. This significantly increases risk of serious health conditions including heart disease, stroke, and diabetes."
                recommendations = [
                    "Consult with a healthcare provider immediately",
                    "Create a structured weight loss plan",
                    "Consider medical supervision for weight loss",
                    "Focus on sustainable lifestyle changes"
                ]
            
            # Calculate pointer position (0-40 BMI range)
            pointer_position = min((bmi / 40) * 100, 100)
            
            return render_template('bmi.html',
                                 age=age,
                                 gender=gender,
                                 height_cm=height_cm if unit_system == 'metric' else None,
                                 weight_kg=weight_kg if unit_system == 'metric' else None,
                                 bmi=bmi,
                                 category=category,
                                 category_class=category_class,
                                 health_description=health_description,
                                 recommendations=recommendations,
                                 pointer_position=pointer_position)
        
        except (ValueError, ZeroDivisionError):
            return render_template('bmi.html', error="Please enter valid measurements")
    
    return render_template('bmi.html')


# ✅ Register/Login form
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        name = request.form.get('signupName')
        email = request.form.get('signupEmail')
        password = request.form.get('signupPassword')
        confirm_password = request.form.get('confirmPassword')
        agree_terms = request.form.get('agreeTerms')

        print("Form submitted")

        # No validation
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users1 WHERE email = %s", (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Email already registered!'
        else:
            cursor.execute(
                "INSERT INTO users1 (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            mysql.connection.commit()
            cursor.close()
            msg = 'You have successfully registered!'
            return redirect(url_for('dashboard'))

    return render_template('login.html', msg=msg)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['loginEmail']
        password = request.form['loginPassword']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password FROM users1 WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            stored_password = result[0]
            if stored_password == password:
                session['email'] = email
                print(stored_password,email)
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password')
                return redirect(url_for('login'))
        else:
            flash('Email not found')
            return redirect(url_for('login'))
    
    # If GET request, render login page
    return render_template('login.html')
# ✅ Dashboard route
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/mental")
def mental():
    return render_template("mental.html")

@app.route("/affirmation")
def affirmation():
    return render_template("affirmation.html")
@app.route("/goal")
def goal():
    return render_template("goal.html")
@app.route("/profile")
def profile():
    return render_template("profile.html")
# ✅ Google OAuth2 login route
@app.route("/welcome")
def welcome():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info.", 500

    user_info = resp.json()
    return render_template("welcome.html", name=user_info["name"], email=user_info["email"])



# Nutritionix API Configuration - Get free key from https://developer.nutritionix.com
NUTRITIONIX_APP_ID = 'fa5d03ba'
NUTRITIONIX_APP_KEY = '9576d856db71fec3320fea6f11045ee7	'

@app.route('/calories', methods=['GET', 'POST'])
def calories():
    """
    Complete calorie calculator with meal plan generation
    """
    result_data = None
    
    if request.method == 'POST':
        try:
            # Get form data
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            height = float(request.form.get('height'))  # cm
            weight = float(request.form.get('weight'))  # kg
            activity_level = float(request.form.get('activity_level'))
            goal = request.form.get('goal')
            diet_preference = request.form.get('diet', '')
            
            # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor
            if gender == 'male':
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
            
            # Calculate TDEE (Total Daily Energy Expenditure)
            tdee = round(bmr * activity_level)
            
            # Calculate calorie goals
            calorie_goals = {
                'maintain': tdee,
                'mild_loss': round(tdee * 0.9),
                'weight_loss': round(tdee * 0.8),
                'extreme_loss': round(tdee * 0.65),
                'mild_gain': round(tdee * 1.1),
                'weight_gain': round(tdee * 1.2)
            }
            
            # Generate zigzag schedule
            zigzag_schedule_1 = [
                {'day': 'Sunday', 'mild': calorie_goals['maintain'], 'moderate': calorie_goals['weight_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Monday', 'mild': calorie_goals['mild_loss'], 'moderate': calorie_goals['extreme_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Tuesday', 'mild': calorie_goals['mild_loss'], 'moderate': calorie_goals['extreme_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Wednesday', 'mild': calorie_goals['mild_loss'], 'moderate': calorie_goals['extreme_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Thursday', 'mild': calorie_goals['mild_loss'], 'moderate': calorie_goals['extreme_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Friday', 'mild': calorie_goals['mild_loss'], 'moderate': calorie_goals['extreme_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Saturday', 'mild': calorie_goals['maintain'], 'moderate': calorie_goals['maintain'], 'extreme': round(calorie_goals['extreme_loss'] * 1.08)}
            ]
            
            zigzag_schedule_2 = [
                {'day': 'Sunday', 'mild': round(calorie_goals['mild_loss'] * 0.95), 'moderate': calorie_goals['extreme_loss'], 'extreme': calorie_goals['extreme_loss']},
                {'day': 'Monday', 'mild': round(calorie_goals['mild_loss'] * 1.03), 'moderate': round(calorie_goals['weight_loss'] * 1.05), 'extreme': round(calorie_goals['extreme_loss'] * 1.02)},
                {'day': 'Tuesday', 'mild': round(calorie_goals['maintain'] * 0.88), 'moderate': round(calorie_goals['maintain'] * 0.78), 'extreme': round(calorie_goals['extreme_loss'] * 1.04)},
                {'day': 'Wednesday', 'mild': calorie_goals['maintain'], 'moderate': calorie_goals['maintain'], 'extreme': round(calorie_goals['weight_loss'] * 0.89)},
                {'day': 'Thursday', 'mild': round(calorie_goals['mild_loss'] * 1.02), 'moderate': round(calorie_goals['weight_loss'] * 1.04), 'extreme': round(calorie_goals['extreme_loss'] * 1.02)},
                {'day': 'Friday', 'mild': round(calorie_goals['mild_loss'] * 0.98), 'moderate': round(calorie_goals['weight_loss'] * 0.96), 'extreme': round(calorie_goals['extreme_loss'] * 0.98)},
                {'day': 'Saturday', 'mild': calorie_goals['maintain'], 'moderate': calorie_goals['maintain'], 'extreme': round(calorie_goals['weight_loss'] * 0.89)}
            ]
            
            # Determine target calories
            if goal == 'lose':
                target_calories = calorie_goals['weight_loss']
            elif goal == 'gain':
                target_calories = calorie_goals['mild_gain']
            else:
                target_calories = calorie_goals['maintain']
            
            result_data = {
                'bmr': round(bmr),
                'tdee': tdee,
                'calorie_goals': calorie_goals,
                'zigzag_schedule_1': zigzag_schedule_1,
                'zigzag_schedule_2': zigzag_schedule_2,
                'target_calories': target_calories,
                'diet_preference': diet_preference,
                'goal': goal
            }
            
        except (ValueError, TypeError) as e:
            result_data = {'error': 'Please enter valid data'}
    
    return render_template("calories.html", result=result_data)

@app.route('/api/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    """
    API endpoint to generate meal plan using Nutritionix
    """
    try:
        data = request.get_json()
        target_calories = int(data.get('target_calories'))
        diet = data.get('diet', '')
        
        # Generate meal suggestions based on calorie target
        meals_per_day = 3
        calories_per_meal = target_calories // meals_per_day
        
        # Define meal types and sample queries
        meal_queries = {
            'breakfast': ['oatmeal with berries', 'eggs and toast', 'greek yogurt parfait', 'avocado toast'],
            'lunch': ['grilled chicken salad', 'turkey sandwich', 'quinoa bowl', 'tuna wrap'],
            'dinner': ['baked salmon with vegetables', 'chicken stir fry', 'lean beef with rice', 'pasta with marinara']
        }
        
        # Adjust queries based on diet preference
        if diet == 'vegetarian':
            meal_queries['breakfast'] = ['oatmeal with nuts', 'vegetable omelet', 'smoothie bowl', 'avocado toast']
            meal_queries['lunch'] = ['chickpea salad', 'vegetable wrap', 'quinoa buddha bowl', 'caprese sandwich']
            meal_queries['dinner'] = ['vegetable stir fry with tofu', 'lentil curry', 'eggplant parmesan', 'veggie pasta']
        elif diet == 'vegan':
            meal_queries['breakfast'] = ['oatmeal with almond milk', 'tofu scramble', 'smoothie bowl', 'chia pudding']
            meal_queries['lunch'] = ['vegan buddha bowl', 'hummus wrap', 'lentil salad', 'veggie sushi']
            meal_queries['dinner'] = ['tofu stir fry', 'vegan curry', 'bean burrito bowl', 'veggie pasta']
        elif diet == 'ketogenic':
            meal_queries['breakfast'] = ['bacon and eggs', 'keto smoothie', 'avocado with salmon', 'cheese omelet']
            meal_queries['lunch'] = ['chicken caesar salad', 'tuna lettuce wrap', 'beef and broccoli', 'cobb salad']
            meal_queries['dinner'] = ['steak with butter', 'salmon with asparagus', 'pork chops', 'chicken thighs']
        
        enhanced_meals = []
        
        # Get nutrition data from Nutritionix for each meal type
        for meal_type, queries in meal_queries.items():
            import random
            query = random.choice(queries)
            
            # Call Nutritionix Natural Language API
            url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
            headers = {
                'x-app-id': NUTRITIONIX_APP_ID,
                'x-app-key': NUTRITIONIX_APP_KEY,
                'Content-Type': 'application/json'
            }
            body = {
                'query': query
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=10)
            
            if response.status_code == 200:
                nutrition_data = response.json()
                
                for food in nutrition_data.get('foods', [])[:1]:  # Get first item
                    enhanced_meals.append({
                        'id': len(enhanced_meals) + 1,
                        'title': food.get('food_name', query).title(),
                        'meal_type': meal_type.title(),
                        'readyInMinutes': 30,
                        'servings': 1,
                        'image': food.get('photo', {}).get('highres', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'),
                        'sourceUrl': '#',
                        'calories': round(food.get('nf_calories', 0)),
                        'protein': round(food.get('nf_protein', 0)),
                        'carbs': round(food.get('nf_total_carbohydrate', 0)),
                        'fat': round(food.get('nf_total_fat', 0)),
                        'serving_size': f"{food.get('serving_qty', 1)} {food.get('serving_unit', 'serving')}"
                    })
            else:
                # Add demo meal if API fails
                enhanced_meals.append(get_demo_meal_for_type(meal_type, len(enhanced_meals) + 1))
        
        if enhanced_meals:
            return jsonify({
                'success': True,
                'meals': enhanced_meals,
                'demo': len(enhanced_meals) < 3
            })
        else:
            return jsonify({
                'success': True,
                'meals': get_demo_meals(),
                'demo': True,
                'message': 'Using demo data. Add valid Nutritionix API key for real recommendations.'
            })
    
    except Exception as e:
        return jsonify({
            'success': True,
            'meals': get_demo_meals(),
            'demo': True,
            'error': str(e)
        })

def get_demo_meal_for_type(meal_type, meal_id):
    """Get demo meal based on type"""
    demo_meals = {
        'breakfast': {
            'id': meal_id,
            'title': 'Avocado Toast with Poached Eggs',
            'meal_type': 'Breakfast',
            'readyInMinutes': 15,
            'servings': 1,
            'image': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=400',
            'calories': 350,
            'protein': 18,
            'carbs': 35,
            'fat': 16,
            'sourceUrl': '#',
            'serving_size': '1 serving'
        },
        'lunch': {
            'id': meal_id,
            'title': 'Grilled Chicken Caesar Salad',
            'meal_type': 'Lunch',
            'readyInMinutes': 25,
            'servings': 1,
            'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400',
            'calories': 450,
            'protein': 42,
            'carbs': 25,
            'fat': 20,
            'sourceUrl': '#',
            'serving_size': '1 serving'
        },
        'dinner': {
            'id': meal_id,
            'title': 'Salmon with Roasted Vegetables',
            'meal_type': 'Dinner',
            'readyInMinutes': 30,
            'servings': 1,
            'image': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400',
            'calories': 520,
            'protein': 38,
            'carbs': 32,
            'fat': 25,
            'sourceUrl': '#',
            'serving_size': '1 serving'
        }
    }
    return demo_meals.get(meal_type, demo_meals['lunch'])

def get_demo_meals():
    """Demo meals when API is not available"""
    return [
        {
            'id': 1,
            'title': 'Avocado Toast with Poached Eggs',
            'meal_type': 'Breakfast',
            'readyInMinutes': 15,
            'servings': 1,
            'image': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=400',
            'calories': 350,
            'protein': 18,
            'carbs': 35,
            'fat': 16,
            'sourceUrl': '#',
            'serving_size': '1 serving'
        },
        {
            'id': 2,
            'title': 'Grilled Chicken Caesar Salad',
            'meal_type': 'Lunch',
            'readyInMinutes': 25,
            'servings': 1,
            'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400',
            'calories': 450,
            'protein': 42,
            'carbs': 25,
            'fat': 20,
            'sourceUrl': '#',
            'serving_size': '1 serving'
        },
        {
            'id': 3,
            'title': 'Salmon with Roasted Vegetables',
            'meal_type': 'Dinner',
            'readyInMinutes': 30,
            'servings': 1,
            'image': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400',
            'calories': 520,
            'protein': 38,
            'carbs': 32,
            'fat': 25,
            'sourceUrl': '#',
            'serving_size': '1 serving'
        }
    ]

@app.route('/api/search-food', methods=['POST'])
def search_food():
    """
    Search for food and get nutrition info using Nutritionix
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'success': False, 'error': 'No query provided'})
        
        # Call Nutritionix Natural Language API
        url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        headers = {
            'x-app-id': NUTRITIONIX_APP_ID,
            'x-app-key': NUTRITIONIX_APP_KEY,
            'Content-Type': 'application/json'
        }
        body = {'query': query}
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        
        if response.status_code == 200:
            nutrition_data = response.json()
            foods = []
            
            for food in nutrition_data.get('foods', []):
                foods.append({
                    'name': food.get('food_name', '').title(),
                    'brand': food.get('brand_name', ''),
                    'serving_qty': food.get('serving_qty', 1),
                    'serving_unit': food.get('serving_unit', ''),
                    'calories': round(food.get('nf_calories', 0)),
                    'protein': round(food.get('nf_protein', 0), 1),
                    'carbs': round(food.get('nf_total_carbohydrate', 0), 1),
                    'fat': round(food.get('nf_total_fat', 0), 1),
                    'fiber': round(food.get('nf_dietary_fiber', 0), 1),
                    'sugar': round(food.get('nf_sugars', 0), 1),
                    'sodium': round(food.get('nf_sodium', 0)),
                    'image': food.get('photo', {}).get('thumb', '')
                })
            
            return jsonify({
                'success': True,
                'foods': foods
            })
        else:
            return jsonify({
                'success': False,
                'error': 'API request failed',
                'foods': []
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'foods': []
        })
    
# ✅ Run app
if __name__ == "__main__":
    app.run(debug=True)
