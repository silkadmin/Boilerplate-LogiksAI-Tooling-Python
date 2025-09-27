module.exports = {
  apps : [{
    name: 'LAI_TOOLING',
    script: 'venv/bin/python main.py',
    instances : '1',
    env: {
        "NODE_ENV": "production"
    }
  }]
};

