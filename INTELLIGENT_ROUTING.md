# 🧠 Intelligent Query Routing

## Overview

DZP IAC Agent now features **intelligent automatic routing** that decides whether to use the standard processor or DeepAgents multi-agent orchestration based on your query complexity.

**You no longer need to manually toggle `USE_DEEPAGENTS`** - the app is smart enough to know when it's needed!

---

## How It Works

### The Intelligence Layer

When you ask a question, the `QueryClassifier` analyzes it for:

1. **Complexity Indicators**
   - Multi-domain requirements (security + cost + compliance)
   - Multi-step workflows (planning, implementation, validation)
   - Strategic keywords (migration, roadmap, comprehensive audit)

2. **Query Patterns**
   - Simple patterns: "Show me...", "What is...", "How many..."
   - Direct commands: "Run terraform plan"
   - Complex requests: "Design a migration strategy..."

3. **Domain Detection**
   - Security domain
   - Cost optimization domain
   - Deployment/migration domain
   - Compliance domain
   - Performance domain

### Routing Decision

Based on the analysis, queries are classified as:

- **SIMPLE** → Standard Processor (fast, 1-3 seconds)
- **MODERATE** → Standard Processor (avoids DeepAgents overhead)
- **COMPLEX** → DeepAgents (multi-agent coordination, 10-30 seconds)

---

## Examples

### ✅ Standard Processor (Simple Queries)

These queries use the **fast standard processor**:

```
❌ DeepAgents NOT needed:

• "What resources are in this configuration?"
• "Show me all S3 buckets"
• "How many VMs do I have?"
• "Run terraform plan"
• "Analyze security of this infrastructure"
• "What's the estimated cost?"
• "List all EC2 instances"
• "Validate the configuration"
```

**Why?** Single-domain, straightforward questions that don't require multi-agent coordination.

---

### ✅ DeepAgents (Complex Queries)

These queries automatically trigger **DeepAgents multi-agent orchestration**:

```
✅ DeepAgents WILL be used:

• "Plan a migration from AWS to Azure with cost analysis and security review"
• "Perform a comprehensive SOC2 compliance audit and create a remediation roadmap"
• "Optimize costs while maintaining security compliance and create implementation plan"
• "Design a blue-green deployment strategy with rollback procedures and cost estimates"
• "Analyze our infrastructure for CIS benchmark violations, estimate remediation costs, and create a 60-day implementation plan"
• "Should I migrate from VMs to Kubernetes? Provide cost comparison, security implications, and migration strategy"
```

**Why?** Multi-domain, multi-step workflows that benefit from coordinated expert agents.

---

## Configuration

### Recommended Setup (Intelligent Routing)

```env
# .env
USE_DEEPAGENTS=true  # Make DeepAgents available
```

With this setting:
- DeepAgents is **available** when needed
- But **only used** for complex queries
- Simple queries use the fast standard processor

### Alternative: Disable DeepAgents Completely

```env
# .env
USE_DEEPAGENTS=false  # Disable DeepAgents entirely
```

With this setting:
- All queries use standard processor
- No DeepAgents initialization overhead
- Faster startup, lower memory usage
- Complex queries still work, just without multi-agent coordination

---

## Classification Logic

### Complexity Scoring

The classifier assigns a complexity score (0.0 to 1.0):

| Score | Decision | Reasoning |
|-------|----------|-----------|
| 0.0 - 0.3 | SIMPLE | Direct questions, single domain |
| 0.3 - 0.6 | MODERATE | Multi-step but manageable with standard processor |
| 0.6+ | COMPLEX | Requires DeepAgents coordination |

### Scoring Factors

**+0.3 points** for each:
- DeepAgents trigger keyword (migrate, audit, roadmap, etc.)
- Additional domain detected (security + cost, cost + compliance)
- Multi-step workflow indicators

**+0.2 points** for:
- Long queries (>30 words)

### DeepAgents Trigger Keywords

```python
'migrate', 'migration', 'comprehensive audit', 'compliance audit',
'soc2', 'hipaa', 'gdpr', 'roadmap', 'strategy', 'optimize cost',
'cost-benefit', 'trade-off', 'risk assessment', 'blue-green',
'phased approach', 'implementation plan', etc.
```

---

## Performance Comparison

### Standard Processor
- ⚡ **Startup:** <1 second
- ⚡ **Response:** 1-3 seconds
- 💰 **API Calls:** 1-3 per query
- 🎯 **Best for:** Simple queries, direct commands

### DeepAgents
- 🤖 **Startup:** 2-3 seconds (4 sub-agents)
- 🤖 **Response:** 10-30 seconds
- 💰 **API Calls:** 5-15 per query
- 🎯 **Best for:** Complex multi-domain workflows

---

## Benefits

### ✅ User Experience
- **No manual configuration** needed
- **Automatic optimization** - fast for simple, powerful for complex
- **Transparent** - logs show which processor is used and why

### ✅ Performance
- **Fast by default** - simple queries aren't slowed down
- **Power when needed** - complex workflows get full multi-agent coordination

### ✅ Cost Efficiency
- **Fewer API calls** for simple queries
- **Optimal resource usage** - only activate DeepAgents when beneficial

---

## Troubleshooting

### "DeepAgents recursion limit" Error

**Problem:** Complex query triggered DeepAgents but hit recursion limit.

**Solution:** The classifier now prevents this by:
1. Filtering vague queries to standard processor
2. Only using DeepAgents for well-defined complex tasks
3. Requiring specific multi-domain indicators

### "All queries use standard processor"

**Problem:** DeepAgents never activates.

**Check:**
1. Is `USE_DEEPAGENTS=true` in `.env`?
2. Are your queries specific enough? (Include keywords like "migration", "audit", "roadmap")
3. Check logs for classification reasoning

### "I want to force DeepAgents"

**Solution:** Make your query more specific:

```
❌ Vague: "Analyze security"
✅ Specific: "Perform a comprehensive SOC2 security audit with remediation roadmap"

❌ Vague: "Check costs"
✅ Specific: "Optimize costs while maintaining compliance and create implementation plan"
```

---

## Logs & Debugging

The app logs routing decisions:

```bash
INFO: ⚡ Using standard processor: Simple query - standard processor is sufficient
INFO: Query: What resources are in this configuration?...

INFO: 🤖 Using DeepAgents: Complex query requiring multi-agent coordination. Confidence: 90%
INFO: Query: Plan a migration from AWS to Azure with cost analysis...
```

Check logs to understand routing decisions.

---

## Technical Details

### Query Classifier Architecture

```python
QueryClassifier
├── classify_query()          # Main classification logic
├── should_use_deepagents()   # Decision function
├── _is_terraform_command()   # Detect direct commands
├── _is_simple_pattern()      # Detect simple queries
├── _check_deepagents_triggers() # Check for complexity keywords
├── _identify_domains()       # Multi-domain detection
└── _has_multi_step_indicators() # Workflow detection
```

### Integration Point

The `EnhancedAIProcessor` calls the classifier before routing:

```python
async def process_request(self, request: str, ...):
    # Intelligent routing
    should_use_deep, reasoning = self.query_classifier.should_use_deepagents(
        request,
        deepagents_available=self.deepagents_processor is not None
    )

    if should_use_deep and self.deepagents_processor:
        return await self.deepagents_processor.process_request(...)
    else:
        return await self.openai_processor.process_request(...)
```

---

## Summary

**Before:** Manual toggle between processors, risk of recursion errors

**Now:** Intelligent automatic routing based on query complexity

**Result:**
- ⚡ Fast for simple queries
- 🤖 Powerful for complex workflows
- 🎯 Optimal resource usage
- 😊 Better user experience

---

## Next Steps

1. Keep `USE_DEEPAGENTS=true` in `.env`
2. Ask questions naturally - the app will route intelligently
3. Check logs to see routing decisions
4. Adjust query wording if you want to force DeepAgents

**The app is now smarter than ever!** 🧠✨
