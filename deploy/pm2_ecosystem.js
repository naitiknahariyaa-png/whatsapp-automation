/**
 * PM2 Ecosystem Configuration
 * Auto-healing process manager for WhatsApp bot
 */

module.exports = {
  apps: [
    {
      name: "whatsapp-bot",
      script: "main.py",
      interpreter: "python3",
      
      // Auto-restart settings
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      
      // Restart delays
      exp_backoff_restart_delay: 100,  // Start with 100ms, exponential
      max_restarts: 10,
      min_uptime: "10s",
      
      // Environment
      env: {
        NODE_ENV: "production"
      },
      env_production: {
        NODE_ENV: "production",
        LOG_LEVEL: "INFO"
      },
      
      // Logging
      log_file: "logs/pm2.log",
      out_file: "logs/pm2-out.log",
      error_file: "logs/pm2-error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      
      // Process management
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 3000,
      
      // Metrics (for PM2 Plus)
      instance_var: "INSTANCE_ID"
    }
  ]
}
