# BNPL Simulator Application

A comprehensive Buy Now, Pay Later (BNPL) simulation system with advanced features including affordability analysis, stress testing, and financing comparisons.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone or download the project**
2. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install frontend dependencies:**
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python run_application.py
   ```

### Alternative Manual Setup

**Start Backend:**
```bash
cd bnpl_simulator
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Start Frontend:**
```bash
cd frontend
streamlit run app.py
```

## 📋 Features Overview

### 🏠 Dashboard
- Central hub for all features
- Quick access to main functionalities
- System status overview

### 👤 User Management
- **User Profile Management**: Complete user information display
- **BNPL Health Score**: Gamified financial health scoring (300-850 range)
- **Settings**: Configure stress events and teen/parental mode

### 💳 Checkout & Loan Management
- **Process Checkout**: Real-time loan approval simulation
- **Pay Installments**: Manage installment payments
- **Loan Dashboard**: Track all active loans with progress visualization

### 📊 Affordability Analysis
- **Basic Analysis**: Simple affordability scoring with recommendations
- **Enhanced Analysis**: Advanced risk assessment with SAFE/BORDERLINE/DANGEROUS classification

### 💰 Financing Comparison
- **BNPL vs Credit Card vs Personal Loan**: Side-by-side comparison
- **Interactive Charts**: Visualize total repayment and monthly payments
- **Personalized Rates**: Based on user credit score

### ⚠️ Stress Testing
- **Stress Event Simulation**: Job loss, medical expense, delayed salary scenarios
- **Refund Scenarios**: Complex refund process simulation

### 🎯 Advanced Features
- **Debt Spiral Visualization**: See consequences of missed payments
- **Social Comparison**: Benchmark against anonymized peer data
- **Advanced Analytics**: System-wide metrics and insights

## 🏗️ Architecture

### Backend (FastAPI)
- **Language**: Python with FastAPI framework
- **Database**: SQLite with SQLAlchemy ORM
- **Features**: 
  - RESTful API endpoints
  - ML-powered risk assessment
  - Real-time loan processing
  - Advanced affordability analysis

### Frontend (Streamlit)
- **Language**: Python with Streamlit framework
- **Visualization**: Plotly for interactive charts
- **Features**:
  - Responsive web interface
  - Real-time data updates
  - Interactive dashboards
  - User-friendly navigation

## 🔌 API Endpoints

### User Management
- `GET /users/{user_id}` - Get user profile
- `GET /users/{user_id}/obligations` - Get active loans
- `GET /users/{user_id}/health-score` - Get BNPL health score
- `PUT /users/{user_id}/stress-event` - Update stress event
- `PUT /users/{user_id}/teen-mode` - Configure teen mode

### Loan Management
- `POST /checkout` - Process new loan
- `POST /loans/{loan_id}/installments/{installment_number}/pay` - Pay installment

### Affordability Analysis
- `POST /affordability-advice` - Basic affordability assessment
- `POST /enhanced-affordability` - Advanced affordability analysis

### Comparisons & Simulations
- `POST /compare-scenarios` - Financing comparison
- `POST /refund-simulation` - Refund scenario simulation
- `POST /debt-spiral` - Debt spiral visualization data
- `POST /social-comparison` - Social comparison data

## 📊 Sample Data

The application includes sample user data with realistic profiles:
- Credit scores ranging from 300-850
- Various income levels and demographics
- Different purchase behaviors and payment histories
- Stress event scenarios

## 🎯 Use Cases

### For Financial Educators
- Teach BNPL concepts and risks
- Demonstrate debt management principles
- Show impact of stress events on finances

### For Product Developers
- Test BNPL product features
- Validate risk assessment algorithms
- Simulate user behavior patterns

### For Financial Institutions
- Understand BNPL market dynamics
- Test stress scenarios
- Develop responsible lending practices

### For Consumers
- Learn about BNPL implications
- Understand affordability assessment
- Compare financing options

## 🔧 Configuration

### Backend Configuration
Edit `bnpl_simulator/config.py`:
```python
# Database settings
DATABASE_URL = "sqlite:///./bnpl_simulator.db"

# ML model paths
RISK_MODEL_PATH = "best_risk_model.joblib"
LOGISTIC_MODEL_PATH = "logistic_regression_model.joblib"

# Fee structures
LATE_FEE_PER_INSTALLMENT = 10.00
CONVENIENCE_FEE_PERCENTAGE = 0.02
```

### Frontend Configuration
Edit `frontend/app.py`:
```python
# API base URL
API_BASE_URL = "http://localhost:8000"

# Chart colors and styling
CHART_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c"]
```

## 🧪 Testing

### Backend Testing
```bash
# Run backend tests
cd bnpl_simulator
python -m pytest tests/
```

### Frontend Testing
```bash
# Test frontend components
cd frontend
streamlit run app.py --server.port 8502
```

### Integration Testing
1. Start backend: `python -m uvicorn bnpl_simulator.main:app --host 127.0.0.1 --port 8000`
2. Start frontend: `cd frontend && streamlit run app.py`
3. Navigate to http://localhost:8501
4. Test all features end-to-end

## 📈 Performance

### Backend Optimizations
- Database indexing for faster queries
- Caching for frequently accessed data
- Optimized ML model loading
- Connection pooling

### Frontend Optimizations
- Efficient data fetching
- Chart rendering optimization
- Responsive design for all screen sizes
- Loading indicators for API calls

## 🔒 Security

### Current Implementation
- No authentication (demo version)
- Input validation and sanitization
- Safe API endpoint construction

### Production Considerations
- Add authentication and authorization
- Implement rate limiting
- Use HTTPS for API communication
- Add input validation middleware

## 🚀 Deployment

### Local Development
```bash
# Run both backend and frontend
python run_application.py
```

### Production Deployment
1. **Backend**: Deploy FastAPI app using Gunicorn/Uvicorn
2. **Frontend**: Deploy Streamlit app using Streamlit Community Cloud or Docker
3. **Database**: Use PostgreSQL instead of SQLite
4. **Environment**: Set proper environment variables

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd bnpl-simulator

# Install dependencies
pip install -r requirements.txt
cd frontend && pip install -r requirements.txt

# Start development servers
python run_application.py
```

## 📚 Documentation

- [Frontend Features](FRONTEND_FEATURES.md) - Comprehensive frontend feature documentation
- [Backend API](http://localhost:8000/docs) - Interactive API documentation
- [Sample Users](bnpl_simulator/data_loader.py) - Information about sample user data

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (requires 3.8+)
- Ensure all dependencies are installed
- Check port 8000 is not in use

**Frontend can't connect to backend:**
- Ensure backend is running on http://localhost:8000
- Check firewall settings
- Verify API_BASE_URL in frontend

**Missing sample data:**
- Run the backend startup process to generate sample users
- Check bnpl_dataset_v2.csv exists in bnpl_simulator directory

### Getting Help
- Check the [Issues](https://github.com/your-repo/issues) section
- Review the API documentation
- Check the frontend feature documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent web framework
- Streamlit team for the powerful data app framework
- SQLAlchemy for database ORM
- Plotly for interactive visualizations
- All contributors and testers
