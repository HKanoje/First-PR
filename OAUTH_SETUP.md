# OAuth Setup Guide

This guide will help you set up GitHub OAuth authentication for the First-PR application.

## Prerequisites

- A GitHub account
- Backend and frontend development environments set up

## Step 1: Create a GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"OAuth Apps"** in the left sidebar
3. Click **"New OAuth App"**
4. Fill in the application details:
   - **Application name**: `First-PR Local Dev` (or any name you prefer)
   - **Homepage URL**: `http://localhost:5173`
   - **Authorization callback URL**: `http://localhost:8000/auth/github/callback`
   - **Application description**: (optional)
5. Click **"Register application"**

## Step 2: Get Your OAuth Credentials

After creating the app, you'll see:
- **Client ID**: Copy this value
- **Client Secret**: Click **"Generate a new client secret"** and copy the generated secret

⚠️ **Important**: Save your Client Secret immediately - you won't be able to see it again!

## Step 3: Configure Backend Environment Variables

Create or update the `.env` file in the `backend/` directory:

```bash
# Backend .env file location: backend/.env

# GitHub OAuth Credentials
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here

# OAuth Redirect URL (must match GitHub OAuth app settings)
OAUTH_REDIRECT_URL=http://localhost:8000/auth/github/callback

# Frontend Origin (for CORS)
FRONTEND_ORIGIN=http://localhost:5173

# JWT Secret (generate a secure random string)
JWT_SECRET=your_secure_random_string_here

# Database file (optional, defaults to app.db)
DATABASE_FILE=app.db

# GitHub API Token (optional, for higher rate limits)
GITHUB_TOKEN=your_github_personal_access_token_here
```

### Generating a Secure JWT Secret

Use one of these methods to generate a secure random string:

**Option 1: Using OpenSSL**
```bash
openssl rand -hex 32
```

**Option 2: Using Python**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `JWT_SECRET`.

## Step 4: Configure Frontend Environment Variables

Create or update the `.env` file in the `frontend/` directory:

```bash
# Frontend .env file location: frontend/.env

# Backend API URL
VITE_API_URL=http://localhost:8000
```

## Step 5: Verify Your Setup

### Backend `.env` Example
```env
GITHUB_CLIENT_ID=Ov23lio07nYOEhlHVqka
GITHUB_CLIENT_SECRET=6a1ca01534fb97cfa8a02703455f71f896783ed8
OAUTH_REDIRECT_URL=http://localhost:8000/auth/github/callback
FRONTEND_ORIGIN=http://localhost:5173
JWT_SECRET=4e99251de8b144d6be576f457f37d6b8f691764246751b49b2fb4fdacc695257
DATABASE_FILE=app.db
```

### Frontend `.env` Example
```env
VITE_API_URL=http://localhost:8000
```

## Step 6: Test the OAuth Flow

1. **Start the backend server**:
   ```bash
   cd backend
   source ../venv/bin/activate  # Activate virtual environment
   uvicorn main:app --reload --port 8000
   ```

2. **Start the frontend server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the authentication**:
   - Open http://localhost:5173 in your browser
   - Click **"Sign in with GitHub"**
   - You should be redirected to GitHub for authorization
   - After authorizing, you'll be redirected back to the app
   - You should see your GitHub avatar and "Profile" link in the header

## Common Issues

### Issue: "Redirect URI mismatch" error

**Solution**: Ensure your OAuth callback URL in GitHub matches exactly:
```
http://localhost:8000/auth/github/callback
```

### Issue: "SessionMiddleware must be installed" error

**Solution**: Make sure you've installed the required dependencies:
```bash
pip install itsdangerous
```

### Issue: CORS errors in browser console

**Solution**: Verify that:
- `FRONTEND_ORIGIN` in backend `.env` is `http://localhost:5173`
- Both servers are running on the correct ports
- You're not mixing `localhost` and `127.0.0.1`

### Issue: "401 Unauthorized" when accessing profile

**Solution**: 
- Clear your browser cookies for localhost
- Try logging in again
- Check that `JWT_SECRET` is set in backend `.env`

## Security Notes

⚠️ **Never commit `.env` files to version control!**

The `.env` files should already be in `.gitignore`. Double-check:

```bash
# Verify .env is ignored
git status

# If .env shows up, add to .gitignore:
echo "backend/.env" >> .gitignore
echo "frontend/.env" >> .gitignore
echo ".env" >> .gitignore
```

## Production Deployment

When deploying to production:

1. **Create a separate GitHub OAuth App** for production with:
   - Homepage URL: Your production frontend URL
   - Callback URL: Your production backend URL + `/auth/github/callback`

2. **Update environment variables** with production values

3. **Use strong secrets**:
   - Generate new `JWT_SECRET` for production
   - Use environment variable management tools (AWS Secrets Manager, Vercel Environment Variables, etc.)

4. **Enable HTTPS**:
   - Update `OAUTH_REDIRECT_URL` to use `https://`
   - Update `FRONTEND_ORIGIN` to use `https://`
   - Set `secure=True` in cookie settings (`auth.py`)

## Additional Resources

- [GitHub OAuth Documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
- [FastAPI OAuth Guide](https://fastapi.tiangolo.com/advanced/security/oauth2/)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)

## Support

If you encounter issues not covered here, please:
1. Check the terminal logs for both backend and frontend
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure all dependencies are installed (`pip install -r requirements.txt` and `npm install`)
