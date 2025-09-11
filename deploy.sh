#!/bin/bash
set -euo pipefail

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      environment="$2"
      shift 2
      ;;
    --profile)
      awsProfile="$2"
      shift 2
      ;;
    --region)
      awsRegion="$2"
      shift 2
      ;;
    --ecs)
      forceECSDeploy="$2"
      shift 2
      ;;
    --help | *)
      echo "Usage: $0 [--region <AWS_REGION>] [--profile <AWS_PROFILE>] [--env <ENVIRONMENT_NAME>] [--ecs <true|false>]"
      exit 0
  esac
done

# === Set defaults ===
projectPath="$(pwd)"
environment="${environment:-dev}"
sourcePath="$projectPath/src/app"
terraformVars="$projectPath/conf/$environment/terraform.tfvars"
tfplan="tfplan"
awsProfile="${awsProfile:-qms}"
awsRegion="${awsRegion:-us-east-1}"
forceECSDeploy="${forceECSDeploy:-false}"
terraformPath="/usr/bin/terraform"
cluster="qms-${environment}-ecs-cluster"
service="qms-${environment}-api"

# === Validations ===
if [[ ! -x "$terraformPath" ]]; then
  echo "❌ Terraform not found at $terraformPath"
  exit 1
fi

if [[ ! -f "$terraformVars" ]]; then
  echo "❌ Terraform vars file not found: $terraformVars"
  exit 1
fi

export AWS_PROFILE="$awsProfile"
echo "📋 AWS Profile: $AWS_PROFILE"
echo "🎯 Environment: $environment"
echo "🌎 Region: $awsRegion"

# === Zip subdirectories in src/app ===
echo "📦 Bundling source code..."
for dir in "$sourcePath"/*/; do
  [[ -d "$dir" ]] || continue
  subdirName="$(basename "$dir")"
  zipPath="$sourcePath/${subdirName}.zip"
  rm -f "$zipPath"
  
  if ! (cd "$dir" && zip -qr "$zipPath" .); then
    echo "❌ Failed to zip: $subdirName"
  fi
done

# === Terraform deploy ===
echo "🛠️  Initializing Terraform..."
"$terraformPath" init -input=false -compact-warnings > /dev/null

echo "⏳ Planning changes..."
"$terraformPath" plan -out "$tfplan" -input=false -var-file="$terraformVars" -compact-warnings > /dev/null

"$terraformPath" show -no-color "$tfplan" > .tfplan.log
echo "📋 To view the plan summary: .tfplan.log"

if ! (grep -F "  # " .tfplan.log | grep -Eq "created|updated|replaced|deleted|destroyed"); then
  terraform_apply="false"
  echo "✅ No changes detected"
else
  terraform_apply="true"
fi

if [[ "$terraform_apply" == "true" ]]; then
  read -p "❓ Do you want to apply these changes? Type 'yes' to continue: " user_input
  if [[ "$user_input" == "yes" ]]; then
    echo "🚀 Applying Terraform changes..."
    if ! "$terraformPath" apply -no-color -input=false "$tfplan" > .tfapply.log 2>&1; then
      echo "❌ Terraform apply failed. Showing log:"
      cat .tfapply.log
    else
      echo "✅ Terraform changes applied successfully: .tfapply.log"
      echo "📝 Terraform outputs:"
      "$terraformPath" output | sed 's/^/   🡆 /'
    fi
  else
    echo "🚫 Skipping terraform apply (no user input)"
    echo "📝 Terraform outputs:"
    "$terraformPath" output | sed 's/^/   🡆 /'
  fi
else
  echo "🚫 Skipping terraform apply (no changes)"
  echo "📝 Terraform outputs:"
  "$terraformPath" output | sed 's/^/   🡆 /'
fi

# === Conditionally force ECS redeploy ===
if [[ "$forceECSDeploy" == "true" ]]; then
  echo "🚀 Forcing ECS service deployment..."
  aws ecs update-service \
    --cluster "$cluster" \
    --service "$service" \
    --force-new-deployment \
    --region $awsRegion \
    | jq -r '
      .service as $s |
      $s.serviceName as $name |
      ($s.deployments[] | select(.status == "PRIMARY")) as $d |
      "Service: \($name)\nTask Definition: \($d.taskDefinition | split("/")[-1])\nRollout Status: \($d.rolloutState)"
    '
  echo "🔁 ECS redeployment triggered"
else
  echo "🚫 Skipping ECS force deployment (use --ecs true to enable)"
fi