const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// PostgreSQL connection pool
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'onyxs',
  password: process.env.DB_PASSWORD || 'dev_password_123',
  database: process.env.DB_NAME || 'onyxs_fitness'
});

// Test database connection on startup
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('❌ Database connection error:', err);
  } else {
    console.log('✅ Database connected successfully at:', res.rows[0].now);
  }
});

// Routes
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'onyxs-backend'
  });
});

app.get('/api/db-test', async (req, res) => {
  try {
    const result = await pool.query('SELECT version()');
    res.json({
      success: true,
      database: 'PostgreSQL',
      version: result.rows[0].version
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🗄️  Database: ${process.env.DB_HOST}:${process.env.DB_PORT}`);
});
