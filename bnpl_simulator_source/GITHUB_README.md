# BNPL Simulator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-orange.svg)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3.35+-yellow.svg)](https://www.sqlite.org)

A comprehensive Buy Now Pay Later (BNPL) simulation platform for education, research, and financial modeling.

## 🚀 Features

### Core Functionality
- **User Management**: Complete user profile management with credit scoring
- **Loan Processing**: Realistic BNPL checkout and loan lifecycle management
- **Installment Tracking**: Payment scheduling and status management
- **Risk Assessment**: AI-powered affordability analysis and risk scoring

### Advanced Analytics
- **Financing Comparisons**: BNPL vs Credit Card vs Personal Loan analysis
- **Stress Testing**: Economic scenario simulation and impact analysis
- **Debt Spiral Visualization**: Compound interest and late fee simulation
- **Social Comparison**: Benchmarking against anonymized user data

### Special Features
- **Teen Mode**: Parental controls and virtual balance management
- **Refund Complexity**: Real-world refund scenario simulation
- **Transparency Layer**: Convenience fee calculations and disclosures
- **AI Affordability Advisor**: Personalized financial guidance

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/bnpl-simulator.git
cd bnpl-simulator
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application

#### Backend API
```bash
python bnpl_simulator/main.py
```
API will be available at `http://localhost:8000`

#### Frontend Dashboard
```bash
streamlit run frontend/app.py
```
Dashboard will be available at `http://localhost:8501`

## 🎯 Quick Start

### 1. Launch the Application
```bash
# Terminal 1: Start backend
python bnpl_simulator/main.py

# Terminal 2: Start frontend
streamlit run frontend/app.py
```

### 2. Explore the Dashboard
Navigate to `http://localhost:8501` and explore:

- **Dashboard**: Quick actions and system overview
- **User Management**: User profiles and health scores
- **Checkout & Loans**: Process new loans and manage payments
- **Affordability Analysis**: Get personalized financial advice
- **Financing Comparison**: Compare different payment options
- **Stress Testing**: Simulate economic scenarios
- **Advanced Features**: Debt spiral and social comparison tools

### 3. Try Sample User IDs
Use these valid user IDs for testing:
- `81bce556-c47a-4786-8456-2404e1113a6e` (Age: 38, Credit Score: 587)
- `7ea84932-2b9f-4269-b4db-e2eaea1114ba` (Age: 18, Credit Score: 757)
- `684cfeda-ee3d-4598-8174-2c3e9fcc80f4` (Age: 19, Credit Score: 405)

## 🏗️ Architecture

### Backend (FastAPI)
```
bnpl_simulator/
├── main.py              # FastAPI application
├── models.py            # Pydantic and SQLAlchemy models
├── database.py          # Database configuration
├── risk_engine.py       # Risk assessment engine
├── ml_model.py          # Machine learning models
├── affordability_engine.py  # Affordability analysis
├── comparison_engine.py     # Financing comparisons
└── data_loader.py       # CSV data loading
```

### Frontend (Streamlit)
```
frontend/
├── app.py              # Streamlit dashboard
└── requirements.txt    # Frontend dependencies
```

### Database
- **SQLite**: Local database with 50,000+ user records
- **Tables**: Users, Loans, Installments
- **Indexes**: Optimized for performance

## 📊 Sample Data

The application includes a comprehensive dataset with:
- **50,000+ user profiles** with realistic financial data
- **Credit scores** ranging from 300-850
- **Income levels** from ₹20,000 to ₹150,000 annually
- **Purchase categories**: Electronics, Fashion, Groceries, etc.
- **Demographic data**: Age, gender, device type, location

## 🔧 API Endpoints

### User Management
- `GET /users/{user_id}` - Get user profile
- `GET /users/{user_id}/health-score` - Get BNPL health score
- `PUT /users/{user_id}/stress-event` - Apply stress event
- `PUT /users/{user_id}/teen-mode` - Configure teen mode

### Loan Management
- `POST /checkout` - Process new BNPL checkout
- `POST /loans/{loan_id}/installments/{installment_number}/pay` - Pay installment
- `GET /users/{user_id}/obligations` - Get user's active loans

### Analytics
- `POST /affordability-advice` - Get affordability assessment
- `POST /compare-scenarios` - Compare financing options
- `POST /debt-spiral` - Simulate debt scenarios
- `POST /social-comparison` - Get social benchmarks

## 🎨 Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=BNPL+Simulator+Dashboard)

### User Management
![User Management](https://via.placeholder.com/800x400?text=User+Management+Interface)

### Affordability Analysis
![Affordability Analysis](https://via.placeholder.com/800x400?text=Affordability+Analysis)

## 🚀 Deployment

### Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access applications
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Production Deployment
1. Set environment variables
2. Use a production WSGI server (uvicorn, gunicorn)
3. Configure reverse proxy (nginx)
4. Set up database backups
5. Implement monitoring and logging

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/bnpl-simulator.git
cd bnpl-simulator

# Create branch for your changes
git checkout -b feature/your-feature-name

# Make your changes and test
# ...

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Frontend Features](FRONTEND_FEATURES.md) - Detailed frontend capabilities
- [Data Analysis](DATABASE_OPTIMIZATION_SUMMARY.md) - Database insights
- [Feature Enhancements](FEATURE_ENHANCEMENT_RECOMMENDATIONS.md) - Future improvements

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
```

**Database Issues**
```bash
# Delete and recreate database
rm bnpl_simulator/bnpl_simulator.db
# Restart application to recreate
```

**Missing Dependencies**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) - Modern, fast web framework
- [Streamlit](https://streamlit.io) - Beautiful data apps
- [Plotly](https://plotly.com/python/) - Interactive visualizations
- [Pandas](https://pandas.pydata.org) - Data manipulation
- [Scikit-learn](https://scikit-learn.org) - Machine learning

## 📞 Contact

For questions, suggestions, or collaboration opportunities:

- **Repository**: [https://github.com/YOUR_USERNAME/bnpl-simulator](https://github.com/YOUR_USERNAME/bnpl-simulator)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/bnpl-simulator/issues)

## ⭐ Support

If you find this project useful, please consider:

- Giving it a star on GitHub ⭐
- Sharing it with others 📢
- Contributing improvements 💡
- Reporting issues or bugs 🐛

---

**Made with ❤️ for financial education and innovation**