# 🤖 DZP IAC Agent - Quick Reference Cheatsheet

A quick reference guide for interacting with the DZP IAC Agent using natural language with OpenAI-compatible models and DeepAgents multi-agent orchestration.

---

## 📋 Table of Contents

1. [Infrastructure State Queries](#infrastructure-state-queries)
2. [Configuration Analysis](#configuration-analysis)
3. [Terraform Operations](#terraform-operations)
4. [Resource Exploration](#resource-exploration)
5. [Security & Best Practices](#security--best-practices)
6. [Planning & Deployment](#planning--deployment)
7. [Troubleshooting](#troubleshooting)
8. [Token Management](#token-management)
9. [Session Management](#session-management)

---

## 🏗️ Infrastructure State Queries

**Check what's actually deployed:**

```
What resources have been created?
What's currently deployed?
Show me what infrastructure exists
List all deployed resources
What's running in my infrastructure?
Are there any resources in the state?
What has been provisioned?
```

**Check specific resource types:**

```
What VMs are deployed?
Show me all storage accounts that exist
List deployed virtual networks
What databases are running?
Which load balancers are active?
```

**Get resource details:**

```
Show me details about the ops-vm
What's the configuration of the storage account?
Tell me about the network security groups
What are the properties of the virtual network?
```

---

## 📁 Configuration Analysis

**Analyze what's defined in code:**

```
What resources are defined in the configuration?
Show me what's in the Terraform files
Analyze the infrastructure configuration
What's defined in main.tf?
Count the resources in my code
What types of resources are configured?
```

**Check variables and outputs:**

```
What variables are defined?
Show me all input variables
What outputs are configured?
List all the variables and their defaults
What can I configure in this setup?
```

**Get provider information:**

```
What providers are being used?
Which cloud provider is this for?
What Azure resources are configured?
Show me provider details
```

---

## ⚙️ Terraform Operations

**Validation:**

```
Validate the configuration
Is my Terraform code valid?
Check for syntax errors
Validate the setup
Is everything configured correctly?
```

**Planning:**

```
Run terraform plan
What changes will be made?
Show me what will happen if I apply
What's the execution plan?
Plan the infrastructure changes
What will Terraform do?
```

**Initialization:**

```
Initialize Terraform
Run terraform init
Set up the Terraform workspace
Download providers
Initialize the backend
```

**Apply (use with caution):**

```
Apply the changes
Deploy the infrastructure
Create the resources
Run terraform apply
Provision the infrastructure
```

**Destroy (use with extreme caution):**

```
Destroy all resources
Tear down the infrastructure
Remove everything
Run terraform destroy
Delete all managed resources
```

---

## 🔍 Resource Exploration

**Count resources:**

```
How many resources are defined?
Count the total resources
What's the resource count?
How many VMs are there?
```

**Filter by type:**

```
Show me all virtual machines
List storage resources
Find all network-related resources
Show compute resources only
What security groups exist?
```

**Search for specific resources:**

```
Find resources with "ops" in the name
Search for production resources
Show me resources tagged with Environment=Dev
Find resources in the East US region
```

**Get resource relationships:**

```
What depends on the virtual network?
Show me resource dependencies
What's connected to the ops-vm?
Explain the resource relationships
```

---

## 🔒 Security & Best Practices

**Security analysis:**

```
Analyze the security of this infrastructure
What are the security concerns?
Check for security vulnerabilities
Are there any public-facing resources?
What ports are exposed?
Review security group rules
Is encryption enabled?
```

**Best practices review:**

```
Review this configuration for best practices
What can I improve?
Are there any anti-patterns?
Suggest optimizations
What should I change?
How can I make this better?
```

**Compliance checks:**

```
Check for compliance issues
Are resources properly tagged?
Is this production-ready?
What's missing for compliance?
Review naming conventions
```

---

## 📊 Planning & Deployment

**Pre-deployment checks:**

```
What will be created if I apply?
How many resources will be added?
What changes are planned?
Is it safe to apply?
Show me the deployment plan
What's the impact of applying?
```

**Cost estimation:**

```
What's the estimated cost?
How much will this infrastructure cost?
What's the most expensive resource?
Optimize for cost
```

**Migration planning:**

```
Should I migrate from VMs to Kubernetes?
How do I move to a different region?
What's the best way to upgrade?
Plan a migration strategy
```

**Scaling questions:**

```
How can I scale this infrastructure?
What's needed for high availability?
Should I add more VMs?
How do I implement auto-scaling?
```

---

## 🐛 Troubleshooting

**Error diagnosis:**

```
Why did the apply fail?
What's wrong with the configuration?
Debug this error
Explain this Terraform error
Why can't I create this resource?
```

**State issues:**

```
Show the Terraform state
Is the state in sync?
What's in the state file?
Check state consistency
Why is the state locked?
```

**Validation problems:**

```
Why is validation failing?
What's the syntax error?
Fix configuration issues
Check for missing required fields
```

---

## 💰 Token Management

**Check usage:**

```
tokens
usage
Show token usage
What's my API cost?
How many tokens have I used?
Show me the cost breakdown
```

**Optimize costs:**

```
How can I reduce token usage?
What's the cache hit rate?
Am I using prompt caching efficiently?
```

---

## 💾 Session Management

**Export/Import:**

```
export my-session.json
import previous-session.json
Save this conversation
Load a previous session
Export the chat history
```

**Session info:**

```
status
Show session statistics
How long have I been using this?
What's my session info?
```

**Utility commands:**

```
help
clear
exit
quit
```

---

## 🧠 Intelligent Query Routing

The app **automatically** chooses between standard and DeepAgents processing based on query complexity:

### ⚡ Simple Queries (Standard Processor - Fast)

These use the **standard processor** for quick responses (1-3 seconds):

```
What resources are in this configuration?
Show me all S3 buckets
How many VMs do I have?
Run terraform plan
Analyze security of this infrastructure
What's the estimated cost?
List all EC2 instances
Validate the configuration
```

**Why fast?** Single-domain, straightforward questions don't need multi-agent coordination.

### 🤖 Complex Queries (DeepAgents - Powerful)

These automatically trigger **DeepAgents multi-agent orchestration** (15-30 seconds):

```
Plan a migration from AWS to Azure with cost analysis and security review
Perform a comprehensive SOC2 compliance audit and create a remediation roadmap
Optimize costs while maintaining security compliance and create implementation plan
Design a blue-green deployment strategy with rollback procedures and cost estimates
Analyze our infrastructure for CIS benchmark violations, estimate remediation costs, and create a 60-day implementation plan
Should I migrate from VMs to Kubernetes? Provide cost comparison, security implications, and migration strategy
```

**Why DeepAgents?** Multi-domain, multi-step workflows benefit from coordinated expert agents:
- **Security Auditor**: Security analysis and compliance checking
- **Cost Optimizer**: Cost optimization and resource sizing
- **Deployment Validator**: Deployment validation and testing
- **Migration Planner**: Infrastructure migration planning

---

## 💡 Pro Tips

### ✅ **DO:**
- Ask questions naturally in plain English
- Be specific about what you want to know
- Use follow-up questions like "why?" or "tell me more"
- Combine queries: "Check if deployed, then validate configuration"
- Ask for explanations: "Explain why this is configured this way"
- **Let the app decide**: Don't worry about which processor to use - intelligent routing handles it!

### ❌ **DON'T:**
- Use exact Terraform syntax in questions (agent understands natural language)
- Worry about command formatting (agent translates for you)
- Repeat the same question (use conversation history)
- Manually toggle DeepAgents on/off (it's automatic now!)

### 🧠 **Understanding Routing:**
- **Trigger words for DeepAgents**: "migrate", "audit", "roadmap", "comprehensive", "plan for", "strategy"
- **Multi-domain queries**: Combining "security + cost", "compliance + migration" triggers DeepAgents
- **Simple is fast**: Single-topic questions always use the fast processor
- **Complex is thorough**: Multi-step workflows get full multi-agent treatment

### 🎯 **Examples of Great Prompts:**

```
"I want to deploy this, but first check if it's valid and show me what will be created"

"What security risks exist, and how can I fix them?"

"Compare the defined resources with what's actually deployed"

"Before I apply, show me the plan and explain any concerning changes"

"What's deployed, what's its status, and what does it cost?"
```

---

## 🔄 Conversation Flow Examples

### Example 1: Pre-Deployment Check
```
You: What resources are defined?
Agent: [Lists 8 resources from config]

You: Are any of them already deployed?
Agent: [Checks state and compares]

You: Run a plan and show me what will be created
Agent: [Executes terraform plan with analysis]

You: Looks good, apply it
Agent: [Confirms and applies with warnings]
```

### Example 2: Security Review
```
You: Analyze the security of my infrastructure
Agent: [Extended thinking analysis]

You: What's the biggest risk?
Agent: [Identifies NSG rule allowing SSH from anywhere]

You: How do I fix it?
Agent: [Provides specific configuration changes]

You: Show me the updated config
Agent: [Displays corrected configuration]
```

### Example 3: Troubleshooting
```
You: Why did my apply fail?
Agent: [Analyzes error output]

You: What resources are actually created?
Agent: [Checks state for partial deployment]

You: How do I clean this up?
Agent: [Suggests terraform destroy or targeted actions]
```

---

## 📚 Quick Reference

| What You Want | Example Prompt |
|---------------|----------------|
| Check deployed resources | `What resources have been created?` |
| Validate config | `Validate the configuration` |
| See what will change | `Run terraform plan` |
| Get help | `help` |
| Check costs | `tokens` |
| Security review | `Analyze the security` |
| Best practices | `What can I improve?` |
| Resource count | `How many VMs are defined?` |
| Save session | `export my-work.json` |
| Clear screen | `clear` |

---

## 🎨 Natural Language Freedom

The agent understands variations and synonyms:

- **"Show me"** = "List" = "Display" = "What are" = "Get"
- **"Created"** = "Deployed" = "Provisioned" = "Exists" = "Running"
- **"Resources"** = "Infrastructure" = "Assets" = "Components"
- **"Check"** = "Validate" = "Verify" = "Confirm" = "Review"

**Be natural, be conversational, be specific!** 🚀

---

## 📖 Related Documentation

- [README.md](../README.md) - Full project documentation
- [CODE_EXPLANATION.md](CODE_EXPLANATION.md) - Detailed code architecture

---

**DZP IAC Agent** - Intelligent Infrastructure as Code automation powered by OpenAI-compatible models and DeepAgents
