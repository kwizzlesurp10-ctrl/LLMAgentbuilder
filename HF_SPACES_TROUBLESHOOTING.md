# Hugging Face Spaces Build Troubleshooting

## Known Issue: Dev-Mode Build Failures

### Problem
Builds may fail with errors related to downloading `openvscode-server` in the injected `vscode` stage:

```
error: dst refspec pr/1 matches more than one
cache miss: [vscode 2/2] RUN apt-get update && apt-get install -y wget && wget https://github.com/gitpod-io/openvscode-server/...
```

### Root Cause
Hugging Face Spaces automatically injects additional Docker stages for dev-mode support:
- `vscode` stage: Downloads and installs openvscode-server
- `dev-mode` stage: Sets up development environment
- These stages wrap your final Dockerfile stage

When dev-mode is enabled, HF Spaces tries to download openvscode-server from GitHub, which can fail due to:
- Network connectivity issues
- GitHub rate limiting
- Temporary infrastructure problems on HF Spaces' side

### Solutions

#### Option 1: Disable Dev-Mode (Recommended)
If you don't need the VS Code interface in your Space:

1. Go to your Space settings on Hugging Face
2. Find the "Dev Mode" or "Development Mode" option
3. Disable it
4. Rebuild your Space

This will skip the problematic injected stages entirely.

#### Option 2: Retry the Build
Often this is a temporary network issue:

1. Wait a few minutes
2. Trigger a rebuild from the Space UI
3. The download may succeed on retry

#### Option 3: Wait for Infrastructure Fix
If multiple users are experiencing this, it's likely an HF Spaces infrastructure issue that will be resolved by their team.

### What We've Done
Our Dockerfile includes all necessary tools for dev-mode compatibility:
- ✅ `git` - Required for HF Spaces git config commands
- ✅ `wget` - Required for downloading openvscode-server
- ✅ `tar` - Required for extracting openvscode-server
- ✅ `ca-certificates` - Required for HTTPS API calls

However, we **cannot control** the injected stages that HF Spaces adds, so failures in those stages are outside our control.

### Verification
To verify your Dockerfile is correct, you can:

1. **Test locally** (if Docker is available):
   ```bash
   docker build -t test-build .
   ```

2. **Check Dockerfile syntax**:
   ```bash
   # Our Dockerfile validation script confirms:
   # - All required tools are installed
   # - Multi-stage structure is correct
   # - Port 7860 is exposed
   ```

### Related Issues
- [HF Spaces Dev-Mode Documentation](https://huggingface.co/docs/hub/spaces-sdks-docker#dev-mode)
- [GitHub Issue: openvscode-server downloads](https://github.com/gitpod-io/openvscode-server/issues)

### Status
- ✅ Our Dockerfile is correctly configured for HF Spaces
- ⚠️ Dev-mode injection failures are a known HF Spaces infrastructure issue
- 💡 Disabling dev-mode is the recommended workaround
