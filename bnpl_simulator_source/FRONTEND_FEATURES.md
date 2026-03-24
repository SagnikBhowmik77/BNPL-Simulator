# BNPL Simulator Frontend Features Documentation

This document provides a comprehensive overview of all frontend features and how they integrate with the backend API.

## Architecture Overview

The frontend is built with **Streamlit** and communicates with a **FastAPI** backend through RESTful API calls. The application provides a complete interface for managing BNPL (Buy Now, Pay Later) simulations with advanced features.

## Feature Dependencies

All features are interconnected and depend on each other for a complete BNPL simulation experience:

### 1. User Management ↔ All Other Features
- **User profiles** are required for loan processing, affordability analysis, and comparisons
- **User health scores** depend on loan history and payment behavior
- **Stress events** and **teen mode** settings affect affordability calculations

### 2. Loan Management ↔ Affordability Analysis
- **Active loans** affect debt-to-income ratios in affordability calculations
- **Payment history** influences user health scores and risk assessments
- **Loan status** updates trigger real-time changes in user profiles

### 3. Affordability Analysis ↔ Financing Comparison
- **Affordability scores** help users choose appropriate financing options
- **Risk factors** are considered when comparing different financing methods
- **Enhanced analysis** provides detailed recommendations for each option

### 4. Stress Testing ↔ All Financial Features
- **Stress events** impact affordability calculations and loan approvals
- **Refund scenarios** affect loan management and user obligations
- **Debt spiral visualization** shows consequences of stress events

## Detailed Feature Breakdown

### 🏠 Dashboard
**Purpose**: Central hub providing overview and quick access to all features

**Key Components**:
- Feature cards with descriptions
- Quick action buttons
- System status indicators

**Backend Integration**: No direct API calls, serves as navigation hub

---

### 👤 User Management

#### User Profile Management
**Purpose**: View and manage comprehensive user information

**Features**:
- Display user demographics (age, gender, income)
- Show financial metrics (credit score, completed loans, late payments)
- View device and browsing information
- Display active loan obligations in expandable format

**Backend API Calls**:
- `GET /users/{user_id}` - Retrieve user profile
- `GET /users/{user_id}/obligations` - Get active loans

**Dependencies**: Required for all other features that need user context

#### BNPL Health Score
**Purpose**: Gamified scoring system showing user's financial health

**Features**:
- Interactive gauge chart showing score (300-850 range)
- Color-coded rating system (Poor to Excellent)
- Positive and negative factor lists
- Real-time updates based on payment behavior

**Backend API Calls**:
- `GET /users/{user_id}/health-score` - Calculate and retrieve health score

**Dependencies**: Depends on user profile and loan history data

#### Settings (Stress Events & Teen Mode)
**Purpose**: Configure simulation parameters and special modes

**Features**:
- **Stress Event Simulation**: Apply job loss, medical expense, or delayed salary events
- **Teen Mode**: Enable virtual balance system for parental control
- Real-time updates to user profile

**Backend API Calls**:
- `PUT /users/{user_id}/stress-event` - Update stress event status
- `PUT /users/{user_id}/teen-mode` - Configure teen mode settings

**Dependencies**: Affects all affordability and risk calculations

---

### 💳 Checkout & Loan Management

#### Process Checkout
**Purpose**: Simulate new BNPL purchases with real-time approval

**Features**:
- Input user ID, merchant ID, and purchase amount
- Option to apply convenience fees
- Real-time approval with warnings
- Display loan details and installment schedule

**Backend API Calls**:
- `POST /checkout` - Process new loan application

**Dependencies**: Requires valid user ID, affects user obligations and health score

#### Pay Installment
**Purpose**: Manage and process installment payments

**Features**:
- Select loan and installment number
- View loan status and installment details
- Process payment with confirmation
- Automatic status updates

**Backend API Calls**:
- `GET /loans/{loan_id}` - Retrieve loan details
- `POST /loans/{loan_id}/installments/{installment_number}/pay` - Process payment

**Dependencies**: Requires existing loans, updates user health score and obligations

#### Loan Dashboard
**Purpose**: View all active loans with comprehensive tracking

**Features**:
- Filter by user ID
- Expandable loan details
- Payment progress tracking with progress bars
- Installment status visualization
- Late fee tracking

**Backend API Calls**:
- `GET /users/{user_id}/obligations` - Get all active loans

**Dependencies**: Shows real-time loan status, affects affordability calculations

---

### 📊 Affordability Analysis

#### Basic Analysis
**Purpose**: Simple affordability assessment with score and recommendations

**Features**:
- Input user ID, purchase amount, and desired term
- Display affordability score (0-100)
- Show estimated monthly payment
- Provide advice message and warnings
- Consider credit score, income, and existing debt

**Backend API Calls**:
- `GET /users/{user_id}` - Get user profile for context
- `POST /affordability-advice` - Get basic affordability assessment

**Dependencies**: Requires user profile, considers existing obligations

#### Enhanced Analysis
**Purpose**: Advanced analysis with detailed risk factors and personalized advice

**Features**:
- **SAFE/BORDERLINE/DANGEROUS** classification system
- Detailed risk factor identification
- Personalized recommendations
- Debt-to-income ratio calculation
- Comprehensive scoring algorithm

**Backend API Calls**:
- `GET /users/{user_id}` - Get user profile
- `GET /users/{user_id}/obligations` - Calculate existing debt
- `POST /enhanced-affordability` - Get detailed analysis

**Dependencies**: Most comprehensive feature, depends on all user and loan data

---

### 💰 Financing Comparison

#### Side-by-Side Comparison
**Purpose**: Compare BNPL vs Credit Card vs Personal Loan options

**Features**:
- Input purchase amount and optional user ID for personalized rates
- Display comparison table with all metrics
- Interactive charts for total repayment and monthly payments
- Detailed breakdown of pros and cons for each option
- Effective APR calculations

**Backend API Calls**:
- `GET /users/{user_id}` - Get credit score for personalized rates
- `POST /compare-scenarios` - Generate comparison data

**Dependencies**: Uses user credit score for personalized rates, shows different financing approaches

---

### ⚠️ Stress Testing

#### Stress Event Simulation
**Purpose**: Apply different stress scenarios to users and observe impact

**Features**:
- Select from Job Loss, Medical Expense, Delayed Salary, or None
- Real-time updates to user profile
- Visual feedback on stress event application
- Impact on future affordability calculations

**Backend API Calls**:
- `GET /users/{user_id}` - View current stress event status
- `PUT /users/{user_id}/stress-event` - Apply stress event

**Dependencies**: Affects all subsequent affordability and risk calculations

#### Refund Scenarios
**Purpose**: Simulate complex refund situations with BNPL complications

**Features**:
- Select loan and refund percentage (0-100%)
- Display refund type (Full, Partial, None)
- Show adjustment method and timeline
- List potential complications
- Realistic BNPL refund process simulation

**Backend API Calls**:
- `GET /loans/{loan_id}` - Get loan details
- `POST /refund-simulation` - Simulate refund scenario

**Dependencies**: Requires existing loans, shows real-world BNPL complexities

---

### 🎯 Advanced Features

#### Debt Spiral Visualization
**Purpose**: Show how missed payments can lead to debt spirals over time

**Features**:
- Input user ID and initial loan amount
- Generate 12-month timeline simulation
- Interactive line charts showing debt balance progression
- Bar charts showing late fees accumulation
- Summary metrics (total cost, recovery time, worst case)

**Backend API Calls**:
- `GET /users/{user_id}` - Get user profile for simulation
- `POST /debt-spiral` - Generate debt spiral data

**Dependencies**: Demonstrates consequences of poor payment behavior

#### Social Comparison
**Purpose**: Benchmark user behavior against anonymized peer data

**Features**:
- Percentile ranking system
- Gauge chart showing relative position
- Average metrics comparison (credit score, debt load, payment timing)
- Benchmark analysis vs peer group
- Privacy-focused anonymized data

**Backend API Calls**:
- `POST /social-comparison` - Get social comparison data

**Dependencies**: Provides context for user's financial behavior

#### Advanced Analytics
**Purpose**: System-wide metrics and insights (demo version)

**Features**:
- Sample system metrics (users, loans, approval rates)
- Loan amount distribution pie chart
- Placeholder for comprehensive analytics

**Backend Integration**: Currently uses sample data, can be extended with real system metrics

---

## Data Flow and Interactions

### User Journey Example

1. **User Management**: Load user profile and view health score
2. **Affordability Analysis**: Check if a $1000 purchase is affordable
3. **Financing Comparison**: Compare BNPL vs Credit Card options
4. **Checkout**: Process the loan if affordable
5. **Loan Management**: Track payments and progress
6. **Stress Testing**: Apply stress event to see impact
7. **Enhanced Analysis**: Re-check affordability after stress event
8. **Debt Spiral**: Visualize consequences of missed payments

### Real-time Updates

- **Health Score**: Updates after each payment or new loan
- **Obligations**: Real-time updates when loans are created or paid
- **Risk Calculations**: Immediate reflection of stress events
- **Comparison Rates**: Personalized based on current user status

## Error Handling and Validation

### Form Validation
- Required field checking
- Numeric input validation
- Range validation for percentages and amounts
- User ID existence verification

### API Error Handling
- Network error detection
- Backend availability checking
- Graceful fallbacks for missing data
- User-friendly error messages

### Data Consistency
- Real-time data synchronization
- Cache invalidation when data changes
- Consistent state across all features

## Performance Considerations

### Caching Strategy
- API response caching where appropriate
- Efficient data fetching with pagination
- Optimized database queries in backend

### Visualization Performance
- Efficient chart rendering with Plotly
- Data aggregation for large datasets
- Responsive design for different screen sizes

### User Experience
- Loading indicators for API calls
- Progress feedback for long operations
- Smooth transitions between pages

## Security Considerations

### API Security
- No authentication in demo version
- Input sanitization and validation
- Safe API endpoint construction

### Data Privacy
- No sensitive data storage in frontend
- Anonymized social comparison data
- Secure API communication

## Future Enhancements

### Potential Additions
- Authentication and authorization
- Real-time notifications
- Advanced reporting and analytics
- Mobile-responsive design improvements
- Integration with real payment systems

### Scalability Improvements
- WebSocket integration for real-time updates
- Advanced caching strategies
- Load balancing for high traffic
- Database optimization for large datasets

This comprehensive frontend provides a complete BNPL simulation experience with interconnected features that work together to demonstrate the complexities and considerations of modern BNPL systems.