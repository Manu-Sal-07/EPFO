/**
 * Vercel Backend Build Configuration (vercelfile.js)
 * 
 * For the PF Compass FastAPI backend deployed as a separate Vercel project.
 * 
 * IMPORTANT: Vercel project Root Directory MUST be set to: backend/
 * 
 * This configuration:
 * 1. Explicitly tells Vercel to treat api/index.py as a Python serverless function
 * 2. Ensures Python 3.12 runtime is used
 * 3. Guarantees dependencies from requirements.txt are installed
 */

module.exports = {
  functions: {
    'api/index.py': {
      runtime: 'python3.12',
      memory: 1024,
      maxDuration: 60,
      // Explicitly include requirements.txt for dependency installation
      env: {
        // Ensure pip install finds requirements.txt
        PIP_TARGET: '/var/task'
      }
    }
  },
  routes: [
    {
      src: '/(.*)',
      dest: '/api/index.py'
    }
  ]
};
