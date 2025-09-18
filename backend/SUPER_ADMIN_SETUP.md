# Super Admin Setup Guide

## 🔐 Super Admin Configuration

To set up your super admin account, you need to update the configuration in `registration_backend.py`:

### 1. Update Super Admin Credentials

Edit the following lines in `Class/backend/registration_backend.py`:

```python
# Super Admin Configuration - ONLY YOU CAN ACCESS
SUPER_ADMIN_EMAIL = "your-actual-email@example.com"  # Replace with your email
SUPER_ADMIN_PASSWORD = "your-secure-password-123"    # Replace with your password
```

### 2. Restart the Backend

After updating the credentials, restart your backend server:

```bash
cd Class/backend
python registration_backend.py
```

### 3. Login as Super Admin

- Use your configured email and password to login
- You will have access to the "👑 Super Admin Dashboard" button
- Only you can access admin features - no one else can become a super admin

## 🚀 Google OAuth Setup (Optional)

To enable Google authentication:

### 1. Create Google OAuth App

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set authorized origins: `http://localhost:3000`
6. Copy the Client ID

### 2. Update Frontend Configuration

Edit `Class/frontend/src/App.tsx` and replace:

```typescript
client_id: 'YOUR_GOOGLE_CLIENT_ID', // Replace with your Google Client ID
```

With your actual Google Client ID.

## 🎯 Features Implemented

### ✅ Super Admin System
- Only you can access admin dashboard
- Super admin role is hardcoded and protected
- No one else can become a super admin

### ✅ Landing Page
- Beautiful landing page with 3 options:
  - Continue as Guest
  - Continue as User  
  - Continue with Google

### ✅ Guest Mode
- Users can browse and take quizzes without registration
- Limited functionality for guest users

### ✅ Google OAuth
- One-click Google authentication
- Automatic user creation for new Google users
- Seamless login experience

## 🔒 Security Features

- Super admin credentials are hardcoded in backend
- Admin endpoints are protected with role validation
- Google OAuth tokens are verified server-side
- No unauthorized access to admin features

## 📱 User Experience

- Clean, modern landing page
- Intuitive navigation flow
- Responsive design for all devices
- Professional UI/UX

Your AI-Powered Quiz System is now ready for production with proper admin controls and authentication options!
