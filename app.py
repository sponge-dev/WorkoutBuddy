from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import openai
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workoutbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Load API keys
with open('api_keys.json', 'r') as f:
    api_keys = json.load(f)

openai.api_key = api_keys['OPENAI_API_KEY']

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.Float)  # in cm
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    fitness_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    progress_entries = db.relationship('Progress', backref='user', lazy=True)
    workout_sessions = db.relationship('WorkoutSession', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    weight = db.Column(db.Float)  # in kg
    body_fat_percentage = db.Column(db.Float)
    muscle_mass = db.Column(db.Float)
    chest = db.Column(db.Float)  # measurements in cm
    waist = db.Column(db.Float)
    hips = db.Column(db.Float)
    arms = db.Column(db.Float)
    thighs = db.Column(db.Float)
    notes = db.Column(db.Text)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_type = db.Column(db.String(20), nullable=False)  # bulk, cut, tone, strength, endurance
    target_weight = db.Column(db.Float)
    target_body_fat = db.Column(db.Float)
    target_date = db.Column(db.Date)
    workout_frequency = db.Column(db.Integer)  # days per week
    workout_duration = db.Column(db.Integer)  # minutes per session
    preferred_exercises = db.Column(db.Text)  # JSON string of preferred exercises
    equipment_available = db.Column(db.Text)  # JSON string of available equipment
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # chest, back, legs, shoulders, arms, core, cardio
    muscle_groups = db.Column(db.Text)  # JSON string of muscle groups
    equipment_needed = db.Column(db.String(100))
    difficulty_level = db.Column(db.String(20))
    instructions = db.Column(db.Text)
    tips = db.Column(db.Text)

class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    goal_type = db.Column(db.String(20))
    duration_weeks = db.Column(db.Integer)
    days_per_week = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    workout_sessions = db.relationship('WorkoutSession', backref='workout_plan', lazy=True)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'))
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    exercises = db.relationship('WorkoutExercise', backref='workout_session', lazy=True, cascade='all, delete-orphan')

class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_session_id = db.Column(db.Integer, db.ForeignKey('workout_session.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Text)  # JSON string for reps per set
    weight = db.Column(db.Text)  # JSON string for weight per set
    rest_time = db.Column(db.Integer)  # seconds
    completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    exercise = db.relationship('Exercise', backref='workout_exercises')

# Helper function to calculate BMI
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/workout-plan')
def workout_plan():
    return render_template('workout_plan.html')

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/api/user', methods=['GET', 'POST'])
def user_api():
    if request.method == 'POST':
        data = request.json
        user = User(
            name=data['name'],
            height=data['height'],
            age=data['age'],
            gender=data['gender'],
            fitness_level=data['fitness_level']
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return jsonify({'message': 'User created successfully', 'user_id': user.id})
    
    # GET request
    user_id = session.get('user_id', 1)  # Default to user 1 for demo
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'name': user.name,
            'height': user.height,
            'age': user.age,
            'gender': user.gender,
            'fitness_level': user.fitness_level
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/progress', methods=['GET', 'POST'])
def progress_api():
    user_id = session.get('user_id', 1)
    
    if request.method == 'POST':
        data = request.json
        progress = Progress(
            user_id=user_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if 'date' in data else datetime.utcnow().date(),
            weight=data.get('weight'),
            body_fat_percentage=data.get('body_fat_percentage'),
            muscle_mass=data.get('muscle_mass'),
            chest=data.get('chest'),
            waist=data.get('waist'),
            hips=data.get('hips'),
            arms=data.get('arms'),
            thighs=data.get('thighs'),
            notes=data.get('notes')
        )
        db.session.add(progress)
        db.session.commit()
        return jsonify({'message': 'Progress recorded successfully'})
    
    # GET request
    progress_entries = Progress.query.filter_by(user_id=user_id).order_by(Progress.date.desc()).all()
    return jsonify([{
        'id': p.id,
        'date': p.date.isoformat(),
        'weight': p.weight,
        'body_fat_percentage': p.body_fat_percentage,
        'muscle_mass': p.muscle_mass,
        'chest': p.chest,
        'waist': p.waist,
        'hips': p.hips,
        'arms': p.arms,
        'thighs': p.thighs,
        'notes': p.notes
    } for p in progress_entries])

@app.route('/api/goals', methods=['GET', 'POST'])
def goals_api():
    user_id = session.get('user_id', 1)
    
    if request.method == 'POST':
        data = request.json
        goal = Goal(
            user_id=user_id,
            goal_type=data['goal_type'],
            target_weight=data.get('target_weight'),
            target_body_fat=data.get('target_body_fat'),
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if 'target_date' in data else None,
            workout_frequency=data.get('workout_frequency', 3),
            workout_duration=data.get('workout_duration', 60),
            preferred_exercises=json.dumps(data.get('preferred_exercises', [])),
            equipment_available=json.dumps(data.get('equipment_available', []))
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({'message': 'Goal created successfully', 'goal_id': goal.id})
    
    # GET request
    goals = Goal.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify([{
        'id': g.id,
        'goal_type': g.goal_type,
        'target_weight': g.target_weight,
        'target_body_fat': g.target_body_fat,
        'target_date': g.target_date.isoformat() if g.target_date else None,
        'workout_frequency': g.workout_frequency,
        'workout_duration': g.workout_duration,
        'preferred_exercises': json.loads(g.preferred_exercises),
        'equipment_available': json.loads(g.equipment_available),
        'created_at': g.created_at.isoformat()
    } for g in goals])

@app.route('/api/generate-workout-plan', methods=['POST'])
def generate_workout_plan():
    user_id = session.get('user_id', 1)
    data = request.json
    
    # Get user info and goals
    user = User.query.get(user_id)
    latest_progress = Progress.query.filter_by(user_id=user_id).order_by(Progress.date.desc()).first()
    active_goal = Goal.query.filter_by(user_id=user_id, is_active=True).first()
    
    # Prepare context for OpenAI
    context = f"""
    Create a detailed workout plan for a {user.gender} user with the following profile:
    - Age: {user.age}
    - Height: {user.height}cm
    - Current weight: {latest_progress.weight if latest_progress else 'Not provided'}kg
    - Fitness level: {user.fitness_level}
    - Goal: {active_goal.goal_type if active_goal else data.get('goal_type', 'general fitness')}
    - Workout frequency: {active_goal.workout_frequency if active_goal else data.get('frequency', 3)} days per week
    - Session duration: {active_goal.workout_duration if active_goal else data.get('duration', 60)} minutes
    - Available equipment: {json.loads(active_goal.equipment_available) if active_goal else data.get('equipment', ['bodyweight'])}
    
    Please provide a structured workout plan that includes:
    1. Weekly schedule with specific days
    2. Exercises for each day with sets, reps, and rest periods
    3. Progressive overload suggestions
    4. Tips for optimal results
    
    Format the response as a detailed plan that's easy to follow.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert fitness trainer and nutritionist with deep knowledge of exercise science, anatomy, and personalized workout programming."},
                {"role": "user", "content": context}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        workout_plan_text = response.choices[0].message.content
        
        # Save the workout plan to database
        workout_plan = WorkoutPlan(
            user_id=user_id,
            name=f"{active_goal.goal_type.title() if active_goal else 'Custom'} Workout Plan",
            description=workout_plan_text,
            goal_type=active_goal.goal_type if active_goal else data.get('goal_type', 'general'),
            duration_weeks=data.get('duration_weeks', 8),
            days_per_week=active_goal.workout_frequency if active_goal else data.get('frequency', 3)
        )
        db.session.add(workout_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Workout plan generated successfully',
            'workout_plan': workout_plan_text,
            'plan_id': workout_plan.id
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate workout plan: {str(e)}'}), 500

@app.route('/api/workout-plans', methods=['GET'])
def get_workout_plans():
    user_id = session.get('user_id', 1)
    plans = WorkoutPlan.query.filter_by(user_id=user_id).order_by(WorkoutPlan.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'goal_type': p.goal_type,
        'duration_weeks': p.duration_weeks,
        'days_per_week': p.days_per_week,
        'created_at': p.created_at.isoformat(),
        'is_active': p.is_active
    } for p in plans])

@app.route('/api/workout-plans/<int:plan_id>/pdf', methods=['GET'])
def export_workout_plan_pdf(plan_id):
    user_id = session.get('user_id', 1)
    plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
    
    if not plan:
        return jsonify({'error': 'Workout plan not found'}), 404
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO
        import re
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(f"<b>{plan.name}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Plan details
        details = f"""
        <b>Goal Type:</b> {plan.goal_type.title() if plan.goal_type else 'General Fitness'}<br/>
        <b>Duration:</b> {plan.duration_weeks} weeks<br/>
        <b>Frequency:</b> {plan.days_per_week} days per week<br/>
        <b>Created:</b> {plan.created_at.strftime('%B %d, %Y')}<br/>
        """
        details_para = Paragraph(details, styles['Normal'])
        story.append(details_para)
        story.append(Spacer(1, 24))
        
        # Plan description
        description_lines = plan.description.split('\n')
        for line in description_lines:
            if line.strip():
                # Format headers
                if any(keyword in line.lower() for keyword in ['day ', 'week ', 'workout']):
                    para = Paragraph(f"<b>{line}</b>", styles['Heading2'])
                else:
                    para = Paragraph(line, styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 6))
        
        doc.build(story)
        buffer.seek(0)
        
        from flask import send_file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{plan.name.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
    except ImportError:
        return jsonify({'error': 'PDF generation not available. Please install reportlab: pip install reportlab'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500

@app.route('/api/workout-sessions', methods=['GET', 'POST'])
def workout_sessions_api():
    user_id = session.get('user_id', 1)
    
    if request.method == 'POST':
        data = request.json
        session_obj = WorkoutSession(
            user_id=user_id,
            workout_plan_id=data.get('workout_plan_id'),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            name=data['name'],
            duration_minutes=data.get('duration_minutes'),
            calories_burned=data.get('calories_burned'),
            notes=data.get('notes'),
            completed=data.get('completed', False)
        )
        db.session.add(session_obj)
        db.session.commit()
        return jsonify({'message': 'Workout session created', 'session_id': session_obj.id})
    
    # GET request - get recent sessions
    sessions = WorkoutSession.query.filter_by(user_id=user_id).order_by(WorkoutSession.date.desc()).limit(10).all()
    return jsonify([{
        'id': s.id,
        'date': s.date.isoformat(),
        'name': s.name,
        'duration_minutes': s.duration_minutes,
        'calories_burned': s.calories_burned,
        'completed': s.completed,
        'notes': s.notes
    } for s in sessions])

@app.route('/api/statistics')
def statistics_api():
    user_id = session.get('user_id', 1)
    
    # Get progress data for charts
    progress_data = Progress.query.filter_by(user_id=user_id).order_by(Progress.date).all()
    workout_sessions = WorkoutSession.query.filter_by(user_id=user_id, completed=True).order_by(WorkoutSession.date).all()
    
    # Calculate statistics
    total_workouts = len(workout_sessions)
    total_minutes = sum(s.duration_minutes for s in workout_sessions if s.duration_minutes)
    avg_duration = total_minutes / total_workouts if total_workouts > 0 else 0
    
    # Weight progress
    weight_data = [{'date': p.date.isoformat(), 'weight': p.weight} for p in progress_data if p.weight]
    
    # Workout frequency by month
    from collections import defaultdict
    monthly_workouts = defaultdict(int)
    for session in workout_sessions:
        month_key = session.date.strftime('%Y-%m')
        monthly_workouts[month_key] += 1
    
    return jsonify({
        'total_workouts': total_workouts,
        'total_minutes': total_minutes,
        'average_duration': round(avg_duration, 1),
        'weight_progress': weight_data,
        'monthly_workouts': dict(monthly_workouts)
    })

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample exercises if none exist
        if Exercise.query.count() == 0:
            sample_exercises = [
                Exercise(name="Push-ups", category="chest", muscle_groups=json.dumps(["chest", "triceps", "shoulders"]), 
                        equipment_needed="bodyweight", difficulty_level="beginner",
                        instructions="Start in plank position, lower body until chest nearly touches floor, push back up"),
                Exercise(name="Squats", category="legs", muscle_groups=json.dumps(["quadriceps", "glutes", "hamstrings"]),
                        equipment_needed="bodyweight", difficulty_level="beginner",
                        instructions="Stand with feet shoulder-width apart, lower into sitting position, return to standing"),
                Exercise(name="Deadlifts", category="back", muscle_groups=json.dumps(["hamstrings", "glutes", "back"]),
                        equipment_needed="barbell", difficulty_level="intermediate",
                        instructions="Stand with feet hip-width apart, hinge at hips to lower bar, return to standing"),
                Exercise(name="Pull-ups", category="back", muscle_groups=json.dumps(["lats", "biceps", "rhomboids"]),
                        equipment_needed="pull-up bar", difficulty_level="intermediate",
                        instructions="Hang from bar with palms facing away, pull body up until chin over bar, lower with control"),
                Exercise(name="Plank", category="core", muscle_groups=json.dumps(["core", "shoulders"]),
                        equipment_needed="bodyweight", difficulty_level="beginner",
                        instructions="Hold push-up position on forearms, keep body straight, engage core")
            ]
            
            for exercise in sample_exercises:
                db.session.add(exercise)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) 