# WorkoutBuddy - Intelligent Fitness Management Platform

A comprehensive fitness application that uses OpenAI's GPT-4.1 to generate structured workout plans, track progress, and provide training consultation. Built with Flask and SQLite for local data management.

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Modern web browser

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure API key in `api_keys.json`:
   ```json
   {
     "OPENAI_API_KEY": "your-key-here"
   }
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open http://localhost:5000

## How It Works

### Core Functionality
- **Profile Management**: User demographics, fitness level, and goal tracking
- **AI-Generated Programs**: GPT-4.1 creates structured training programs based on user parameters
- **Progress Tracking**: Weight, body measurements, and performance metrics
- **Session Logging**: Historical workout data with completion tracking
- **Training Consultation**: AI-powered fitness guidance via chat interface

### Workflow
1. User creates profile with demographics and fitness goals
2. AI generates personalized training program using professional formatting
3. User logs workout sessions and progress data
4. System provides analytics and progress visualization
5. AI adapts recommendations based on historical data

## Database Architecture

The application uses SQLite with the following schema:

### Core Tables
- **Users**: Demographics, fitness level, preferences
- **Goals**: Training objectives, frequency, equipment availability
- **Progress**: Weight tracking, body measurements, daily notes
- **WorkoutPlans**: AI-generated training programs with metadata
- **WorkoutSessions**: Individual workout instances with completion status
- **WorkoutExercises**: Exercise details linked to sessions
- **Exercises**: Exercise database with instructions and targeting

### Data Storage
- **Database File**: `workoutbot.db` (created on first run)
- **Location**: Project root directory
- **Backup**: Copy the .db file to preserve data
- **Migration**: Self-initializing schema on startup

## Technical Stack

### Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite for portability
- **AI Integration**: OpenAI GPT-4.1 API
- **PDF Generation**: ReportLab for workout plan exports

### Frontend
- **UI**: Bootstrap 5 responsive design
- **Charts**: Chart.js for data visualization
- **JavaScript**: ES6+ for dynamic interactions
- **CSS**: Custom theme with modern color palette

### Dependencies
Key packages from requirements.txt:
- Flask, Flask-SQLAlchemy, Flask-CORS
- OpenAI SDK (1.55.0+)
- ReportLab for PDF generation
- NumPy, Pandas for data processing
- Plotly for advanced visualizations

## Features

### Training Program Generation
- Structured workout plans using GPT-4.1
- Professional formatting with exercise specifications
- Equipment-specific adaptations
- Progressive overload protocols

### Progress Analytics
- Weight and body composition tracking
- Training frequency analysis
- Goal achievement monitoring
- Visual progress charts

### Data Management
- Local data storage for privacy
- CSV export capabilities
- PDF workout plan generation
- Historical session tracking

### Mobile Support
- Responsive design for all devices
- Touch-optimized interface
- Cross-platform compatibility

## Configuration

### API Setup
Create `api_keys.json` in project root:
```json
{
  "OPENAI_API_KEY": "sk-your-openai-key"
}
```

### Environment Variables (Optional)
- `FLASK_ENV`: Set to 'development' for debug mode
- `SECRET_KEY`: Flask session security (uses default if not set)

## Development

### File Structure
```
WorkoutBuddy/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── api_keys.json      # API configuration
├── workoutbot.db      # SQLite database (auto-created)
├── static/            # CSS, JS, assets
├── templates/         # HTML templates
└── README.md          # Documentation
```

### Database Operations
```bash
# Backup database
cp workoutbot.db backup_$(date +%Y%m%d).db

# Reset database (deletes all data)
rm workoutbot.db
python app.py
```

### API Endpoints
- `GET /`: Main application interface
- `POST /api/generate-workout-plan`: AI program generation
- `GET/POST /api/progress`: Progress data management
- `GET/DELETE /api/workout-plans`: Program management
- `POST /api/chatbot`: Training consultation

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies installed via pip
2. **API Failures**: Verify OpenAI key and account balance
3. **Database Errors**: Delete workoutbot.db to reset schema
4. **Mobile Access**: Use computer's IP address, not localhost

### Performance
- Database optimized for single-user operation
- Responsive design tested on mobile devices
- Charts render efficiently with moderate data volumes

## Security

- All data stored locally (no cloud synchronization)
- OpenAI API calls encrypted in transit
- Session management for user state
- No external data transmission except AI API calls

## License

MIT License - see LICENSE file for details. 