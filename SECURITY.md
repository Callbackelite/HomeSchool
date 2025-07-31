# Security Guide for Savage Homeschool OS

## Default Credentials

⚠️ **IMPORTANT**: The application comes with default credentials that should be changed immediately after installation.

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`

### Default Child Account
- **Username**: `child`
- **PIN**: `1234`

## Security Recommendations

### 1. Change Default Credentials Immediately

After your first login as admin:

1. **Change the admin password**:
   - Go to Admin Dashboard → User Management
   - Click "Edit" on the admin user
   - Set a strong password (minimum 8 characters, mix of letters, numbers, symbols)

2. **Change child PINs**:
   - Go to Admin Dashboard → User Management
   - Click "Edit" on child users
   - Set unique 4-digit PINs for each child

### 2. Environment Variables

Create a `.env` file in the project root with secure values:

```bash
# Copy env.example to .env and modify
cp env.example .env
```

**Required changes**:
- `SECRET_KEY`: Generate a strong random key
- `DATABASE_URL`: Use a secure database in production

**Optional but recommended**:
- Set API keys for external integrations
- Enable secure cookies in production

### 3. Production Deployment

For production use:

1. **Use HTTPS**: Set `SESSION_COOKIE_SECURE=true`
2. **Strong Secret Key**: Generate a cryptographically secure random key
3. **Database Security**: Use PostgreSQL or MySQL instead of SQLite
4. **Regular Backups**: Ensure backup system is working
5. **Firewall**: Restrict access to necessary ports only

### 4. API Key Security

If using external APIs:
- Store API keys in environment variables
- Never commit API keys to version control
- Rotate API keys regularly

### 5. User Management

- Regularly review user accounts
- Deactivate unused accounts
- Monitor login attempts
- Use strong passwords for all accounts

## Security Features

The application includes:
- Password hashing with bcrypt
- Session management with Flask-Login
- CSRF protection
- Input validation and sanitization
- Activity logging for audit trails

## Reporting Security Issues

If you discover a security vulnerability:
1. **Do not** create a public issue
2. Contact the maintainer privately
3. Provide detailed reproduction steps
4. Allow time for assessment and fix

## Updates

Keep the application updated:
- Regularly check for updates
- Apply security patches promptly
- Test updates in development before production 