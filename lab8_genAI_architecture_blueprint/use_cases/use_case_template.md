# Use Case Template

Fill this out to define your GenAI project.

---

## 1. Use Case Name

**Name:** [Give your project a clear, memorable name]

**Examples:**

- "SmartContract AI" (for legal)
- "ResearchGPT" (for research assistant)
- "KnowledgeHub AI" (for internal search)

---

## 2. Problem Statement (3-5 sentences)

**Instructions:** Describe the problem clearly. Focus on:

- What's broken or inefficient?
- Who is affected?
- What's the impact (time, money, quality)?
- Why traditional solutions fall short?

**Your Answer:**

```
[Write your problem statement here]








```

**Example:**

```
Legal teams at mid-size companies spend 20+ hours per week reviewing
contracts for compliance risks. This manual process is error-prone,
expensive ($150/hour labor cost), and creates bottlenecks in deal flow.
Current contract management tools only provide storage and search - they
don't actually analyze content or flag risks.
```

---

## 3. Target Users

**Instructions:** Who will use this system? Be specific about roles.

**Your Answer:**

```
Primary Users:
- [User type 1 and their role]
- [User type 2 and their role]

Secondary Users:
- [User type 3]
- [User type 4]
```

**Example:**

```
Primary Users:
- Contract attorneys (review and approve contracts)
- Legal operations managers (oversee contract workflow)

Secondary Users:
- Compliance officers (ensure regulatory adherence)
- Executives (get risk summaries)
```

---

## 4. Current Solution & Limitations

**Instructions:** How is this done today? What are the pain points?

**Current Approach:**

```
[How is this problem currently solved?]


```

**Key Limitations:**

```
1. [Limitation 1]

2. [Limitation 2]

3. [Limitation 3]

4. [Limitation 4]
```

**Example:**

```
Current Approach:
Lawyers manually read each contract, highlight risky clauses in Word,
and write summary memos. Senior partners review for final approval.

Key Limitations:
1. Slow - Takes 4-6 hours per contract
2. Expensive - $600-900 in labor costs per contract
3. Inconsistent - Different lawyers flag different things
4. Not scalable - Can't handle M&A due diligence (100+ contracts)
```

---

## 5. Proposed GenAI Solution

**Instructions:** Describe your AI system in clear, specific terms.

**Solution Name:**

```
[Your AI system's name]
```

**What it does:**

```
1. [Capability 1]

2. [Capability 2]

3. [Capability 3]

4. [Capability 4]

5. [Capability 5]
```

**Example:**

```
Solution Name: ContractIQ

What it does:
1. Ingests contracts in PDF/DOCX format via web upload
2. Extracts and classifies all clauses (indemnity, termination, IP, etc.)
3. Flags high-risk clauses based on company policy knowledge base
4. Generates executive summary with risk score
5. Suggests alternative language for risky clauses
```

---

## 6. Data & Knowledge Requirements

**Instructions:** What data/knowledge does your system need?

**Data Sources:**

```
1. [Data type] - [Where it comes from] - [Approximate volume]

2. [Data type] - [Where it comes from] - [Approximate volume]

3. [Data type] - [Where it comes from] - [Approximate volume]
```

**Example:**

```
1. Historical contracts - Company archives - 2,000 contracts
2. Company policies - Legal department docs - 50 policy documents
3. Clause library - Legal templates - 200 standard clauses
4. Legal ontology - Build from scratch - Define relationships
5. Industry standards - Public legal databases - Ongoing updates
```

---

## 7. Success Metrics

**Instructions:** How will you measure success? Be specific and quantifiable.

**Metrics:**

**Efficiency Gains:**

```
Current: [Baseline metric]
Target:  [Goal with AI]
```

**Quality Improvements:**

```
Current: [Baseline metric]
Target:  [Goal with AI]
```

**Cost Savings:**

```
Current: [Baseline cost]
Target:  [Goal with AI]
Calculation: [Show your math]
```

**User Satisfaction:**

```
Current: [Baseline]
Target:  [Goal]
Measurement: [How you'll measure]
```

**Example:**

```
Efficiency Gains:
Current: 5 hours per contract
Target:  30 minutes per contract (90% reduction)

Quality Improvements:
Current: 75% of risk clauses identified (manual review)
Target:  95% of risk clauses identified (AI + human review)

Cost Savings:
Current: $750 per contract (5 hours × $150/hour)
Target:  $150 per contract (30 min × $150 + $75 AI cost)
Calculation: $600 savings × 200 contracts/year = $120K/year

User Satisfaction:
Current: 60% satisfaction with review process
Target:  85% satisfaction
Measurement: Quarterly survey
```

---

## 8. Why GenAI vs. Traditional Approaches?

**Instructions:** Explain why AI is the right solution.

**Why Not Just:**

**[Alternative 1]?**

```
[Why this won't work]
```

**[Alternative 2]?**

```
[Why this won't work]
```

**Why GenAI is Better:**

```
[Your reasoning]
```

**Example:**

```
Why Not Just:

Hire more lawyers?
- Cost: $150K/year per lawyer, need 3 = $450K
- AI cost: $50K/year = 90% cheaper
- Scaling: Can't hire fast enough for M&A spikes

Use rule-based software?
- Rigid: Can't understand context or nuance
- Brittle: Breaks when contracts use different language
- Limited: Can't explain reasoning or suggest alternatives

Why GenAI is Better:
- Understands natural language and context
- Learns from feedback
- Can explain its reasoning
- Handles edge cases gracefully
- Scales instantly
```

---

## 9. Key Assumptions & Risks

**Instructions:** What could go wrong? What are you assuming?

**Assumptions:**

```
1. [Assumption 1]

2. [Assumption 2]

3. [Assumption 3]
```

**Risks:**

```
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to handle] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to handle] |
```

**Example:**

```
Assumptions:
1. We can get access to 2,000 historical contracts for training
2. Legal team will provide feedback to improve the system
3. LLM costs will remain stable or decrease

Risks:
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AI hallucinates legal advice | High | Medium | Human-in-loop for all outputs |
| Insufficient training data | Medium | Low | Start with smaller scope |
| LLM costs exceed budget | Medium | Medium | Cache results, use cheaper models |
| User adoption resistance | Medium | Medium | Training + show quick wins |
```

---

## ✅ Completion Checklist

Before moving to architecture design, verify:

- [ ] Problem statement is clear and specific
- [ ] Target users are well-defined
- [ ] Current limitations are documented
- [ ] Solution capabilities are concrete
- [ ] Data requirements are identified
- [ ] Success metrics are quantifiable
- [ ] You can explain why AI is the right approach
- [ ] Key risks are identified with mitigation plans

---

## Next Step

Once this is complete, move to:
**architecture/architecture_template.drawio**

You're ready to design your system! 🎨
