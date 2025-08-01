# Tutorbot CI/CD Deployment

This directory contains the deployment configuration for the Tutorbot CI/CD pipeline.

## Setup Instructions

### 1. GitHub Repository Secrets

You need to add the following secrets to your GitHub repository:

1. Go to your repository: `https://github.com/stephenadei/tutorbot`
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Add the following repository secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `HOST` | Your server's IP address or hostname | `123.456.789.012` |
| `USERNAME` | SSH username | `stephen` |
| `SSH_KEY` | Your private SSH key | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `PORT` | SSH port (optional, defaults to 22) | `22` |

### 2. SSH Key Setup

If you don't have an SSH key pair yet:

```bash
# Generate a new SSH key pair
ssh-keygen -t ed25519 -C "github-actions@tutorbot"

# Copy the public key to your server
ssh-copy-id -i ~/.ssh/id_ed25519.pub stephen@your-server-ip

# Copy the private key content for GitHub secret
cat ~/.ssh/id_ed25519
```

### 3. Server Requirements

Make sure your server has:
- Python 3.11+
- pip3
- git
- sudo access for the deployment user

### 4. How It Works

1. **Push to master/main branch** triggers the workflow
2. **GitHub Actions** runs tests and syntax checks
3. **SSH connection** to your server
4. **Pull latest code** from the repository
5. **Install dependencies** with pip3
6. **Setup systemd service** (first time only)
7. **Restart the service** to apply changes
8. **Verify deployment** and show status

### 5. Manual Deployment

You can also trigger deployment manually:

1. Go to "Actions" tab in your repository
2. Click on "Deploy Tutorbot" workflow
3. Click "Run workflow" → "Run workflow"

### 6. Service Management

Once deployed, you can manage the service with:

```bash
# Check status
sudo systemctl status tutorbot.service

# View logs
sudo journalctl -u tutorbot.service -f

# Restart manually
sudo systemctl restart tutorbot.service

# Stop service
sudo systemctl stop tutorbot.service

# Start service
sudo systemctl start tutorbot.service
```

### 7. Troubleshooting

If deployment fails:

1. Check GitHub Actions logs for detailed error messages
2. Verify SSH connection works: `ssh stephen@your-server-ip`
3. Check if the tutorbot directory exists: `/home/stephen/tutorbot`
4. Verify Python and pip are installed: `python3 --version && pip3 --version`
5. Check service logs: `sudo journalctl -u tutorbot.service -n 50` 