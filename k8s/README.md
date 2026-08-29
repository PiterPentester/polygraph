# Polygraph Telegram Bot - Kubernetes Deployment Guide

This directory contains production Kubernetes manifests to deploy the **Polygraph Spy Game** Telegram bot.

---

## 1. Quick Start

### Step 1: Create the Secret
Create your secret using `kubectl` or by copying `secret.yaml.template`:

```bash
kubectl create secret generic polygraph-secrets \
  --from-literal=BOT_TOKEN="your_telegram_bot_token"
```

Or edit `k8s/secret.yaml` and apply:
```bash
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your token
kubectl apply -f k8s/secret.yaml
```

### Step 2: Apply ConfigMap & Deployment

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
```

### Step 3: Verify Deployment

```bash
kubectl get pods -l app=polygraph-bot
kubectl logs -f -l app=polygraph-bot
```

---

## 2. Adding Custom Question Files

Questions are loaded automatically from the `/app/assets` directory. To add more questions to the cluster:

1. **Option A: Rebuild Docker image**
   Drop any new CSV file into `assets/` (e.g. `assets/my_new_theme.csv`) and rebuild the image:
   ```bash
   make docker-build
   ```

2. **Option B: ConfigMap Volume Mount**
   Mount additional CSV files as a Kubernetes ConfigMap into `/app/assets/`.
