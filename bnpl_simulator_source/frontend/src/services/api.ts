import axios from 'axios';

// API base URL - adjust based on your backend setup
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add any authentication headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// User API endpoints
export const userApi = {
  // Get user profile
  getUser: (userId: string) => api.get(`/users/${userId}`),
  
  // Get user obligations (active loans)
  getUserObligations: (userId: string) => api.get(`/users/${userId}/obligations`),
  
  // Get user health score
  getUserHealthScore: (userId: string) => api.get(`/users/${userId}/health-score`),
  
  // Update stress event
  updateStressEvent: (userId: string, eventType: string) => 
    api.put(`/users/${userId}/stress-event`, { event_type: eventType }),
  
  // Update teen mode
  updateTeenMode: (userId: string, isTeenMode: boolean, virtualBalance?: number) =>
    api.put(`/users/${userId}/teen-mode`, { 
      is_teen_mode: isTeenMode, 
      virtual_balance: virtualBalance 
    }),
  
  // Get social comparison
  getSocialComparison: (userId: string) => 
    api.post('/social-comparison', { user_id: userId }),
};

// Loan API endpoints
export const loanApi = {
  // Process checkout
  processCheckout: (checkoutData: {
    user_id: string;
    merchant_id: string;
    amount: number;
    apply_convenience_fee: boolean;
  }) => api.post('/checkout', checkoutData),
  
  // Pay installment
  payInstallment: (loanId: string, installmentNumber: number) =>
    api.post(`/loans/${loanId}/installments/${installmentNumber}/pay`),
  
  // Get loan by ID
  getLoan: (loanId: string) => api.get(`/loans/${loanId}`),
};

// Affordability API endpoints
export const affordabilityApi = {
  // Get affordability advice
  getAffordabilityAdvice: (userId: string, purchaseAmount: number, desiredTermMonths?: number) =>
    api.post('/affordability-advice', {
      user_id: userId,
      purchase_amount: purchaseAmount,
      desired_term_months: desiredTermMonths
    }),
  
  // Get enhanced affordability analysis
  getEnhancedAffordability: (userId: string, purchaseAmount: number, desiredTermMonths?: number) =>
    api.post('/enhanced-affordability', {
      user_id: userId,
      purchase_amount: purchaseAmount,
      desired_term_months: desiredTermMonths
    }),
  
  // Simulate refund scenario
  simulateRefund: (loanId: string, refundPercentage: number) =>
    api.post('/refund-simulation', {
      loan_id: loanId,
      refund_percentage: refundPercentage
    }),
  
  // Get debt spiral data
  getDebtSpiral: (userId: string, initialLoanAmount: number) =>
    api.post('/debt-spiral', {
      user_id: userId,
      initial_loan_amount: initialLoanAmount
    }),
};

// Comparison API endpoints
export const comparisonApi = {
  // Get financing comparison
  getComparison: (purchaseAmount: number, userId?: string) =>
    api.post('/compare-scenarios', {
      purchase_amount: purchaseAmount,
      user_id: userId
    }),
};

// Export all API functions
export default {
  user: userApi,
  loan: loanApi,
  affordability: affordabilityApi,
  comparison: comparisonApi,
};