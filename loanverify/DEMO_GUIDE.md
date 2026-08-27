# 🎬 LoanVerify — Complete Demo Guide
## Intain FinTech Challenge 2026

---

## ⏱️ Total Time: 8-10 minutes

---

## PART 1: START THE PROJECT (1 minute)

### Terminal Commands (copy-paste these)

**Open Terminal 1 — Backend:**
```bash
cd ~/Documents/Hackerrank_assignment/loanverify/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Open Terminal 2 — Frontend:**
```bash
cd ~/Documents/Hackerrank_assignment/loanverify/frontend
npm run dev
```

**Open Browser:**
```
http://localhost:3000
```

---

## PART 2: DEMO SCRIPT (8 minutes)

---

### 🎤 STEP 1: Opening (30 seconds)

**Say this:**
> "Hi, I'm [YOUR NAME]. Today I'll demo LoanVerify — an AI-powered Loan Data Verification Copilot built for the Intain FinTech Challenge 2026.
>
> The problem: Financial institutions receive messy loan data from multiple sources. This data has errors, outliers, and inconsistencies. Currently, humans manually review every row — slow and error-prone.
>
> Our solution: Upload a messy loan tape, and LoanVerify automatically normalizes it, validates it, explains issues with AI, and creates a tamper-evident audit trail."

**Action:** Show the login page on screen.

---

### 🎤 STEP 2: Login & Roles (45 seconds)

**Say this:**
> "We have three user roles with different permissions."

**Do this:**
1. Click the **analyst** button (auto-fills credentials)
2. Click **Sign In**
3. Point to the sidebar — show the blue "analyst" role badge

**Say this:**
> "As an Analyst, I can upload files and view my data, but I cannot resolve exceptions — that's a Reviewer's job. This ensures proper separation of duties."

---

### 🎤 STEP 3: CSV Preview — NEW FEATURE (1 minute)

**Say this:**
> "Let me show our CSV Preview feature. Before processing, you can see exactly what the system detects."

**Do this:**
1. Click **Upload Data** in sidebar
2. Drag `clean_data.csv` onto the upload zone
   - File location: `loanverify/backend/sample_data/clean_data.csv`
3. **Wait for preview to load** (1 second)

**Point to screen and say:**
> "Look at this — the system automatically detected 13 columns and mapped them to our standard schema. It shows data types, sample values, and null counts. You can review this before committing to process."

**Do this:**
4. Click **Process & Validate**
5. Wait for processing

**Say this:**
> "20 records processed. Quality score: 98 out of 100. Only 7 minor issues."

---

### 🎤 STEP 4: Messy Bank Export (1.5 minutes)

**Say this:**
> "Now let's upload a realistic bank export with completely different column names."

**Do this:**
1. Click **Upload Another File**
2. Drag `messy_bank_export.csv` onto the upload zone
   - File location: `loanverify/backend/sample_data/messy_bank_export.csv`
3. **Show the preview** — point out the column mappings

**Say this:**
> "Notice: `Acct #` maps to `loan_id`, `APR %` maps to `interest_rate`, `Disb Date` maps to `origination_date`. The system handles 50+ naming conventions automatically."

**Do this:**
4. Click **Process & Validate**
5. Click **View Details & Exceptions**

**Say this:**
> "35 records processed. The system found exceptions — let me show you."

**Do this:**
6. Show the exception cards (point to critical ones)

---

### 🎤 STEP 5: AI Explanation (1.5 minutes)

**Say this:**
> "Here's where AI comes in. Every exception gets an explanation."

**Do this:**
1. Find the exception with **45% interest rate** (critical)
2. Click **Explain** button
3. Wait for AI explanation

**Say this:**
> "The AI explains: 'The interest rate of 45% is outside the expected range. This could indicate a data entry error — perhaps a missing decimal point.' This saves reviewers hours of manual investigation."

**Do this:**
4. Find another exception (missing borrower name)
5. Click **Explain** on that too

**Say this:**
> "The AI also suggests fixes. But remember — AI advises, humans decide. The reviewer always makes the final call."

---

### 🎤 STEP 6: Bulk Operations — NEW FEATURE (1 minute)

**Say this:**
> "Now let me show bulk operations. When you have 30+ exceptions, resolving one-by-one is painful."

**Do this:**
1. Click the **checkbox** next to 3-4 exception cards
2. Show the bulk action bar appearing at the top
3. Click **Explain All** button
4. Wait for processing

**Say this:**
> "All 3 exceptions explained in one click. Now let me bulk resolve them."

**Do this:**
5. Click **Resolve All** button
6. Show the exceptions disappear from the pending list

**Say this:**
> "Bulk operations make the reviewer workflow 10x faster."

---

### 🎤 STEP 7: Export — NEW FEATURE (1 minute)

**Say this:**
> "Reviewers need to download clean data. We have 4 export options."

**Do this:**
1. Show the **Export Data** section at the top
2. Click **Verified CSV** button
3. Show the file downloads

**Say this:**
> "Verified CSV contains only records with no unresolved issues. Perfect for downstream systems."

**Do this:**
4. Click **Audit Report** button
5. Open the downloaded JSON file
6. Show the structure: records, exceptions, audit trail, hash chain

**Say this:**
> "This is a complete audit report — every record, every exception, every action logged. Ready for compliance reviews."

---

### 🎤 STEP 8: Hash Chain & Audit (1 minute)

**Say this:**
> "Every record is cryptographically linked."

**Do this:**
1. Click **Audit & Hash Chain** tab
2. Click **Verify Chain** button
3. Show the green "Chain Integrity Verified ✓" message

**Say this:**
> "All 35 records verified. Each record's hash depends on the previous — just like a blockchain, but without the infrastructure. If anyone tampers with one record, the entire chain breaks."

**Do this:**
4. Show the Audit Log entries below
5. Point out the timestamped actions

---

### 🎤 STEP 9: AI Chat — NEW FEATURE (1 minute)

**Say this:**
> "Our AI Copilot also has a chat interface for follow-up questions."

**Do this:**
1. Click on any exception card to open detail view
2. Show the **AI Copilot Chat** panel on the right
3. Click a quick question: **"Is this a false positive?"**
4. Show the AI response

**Say this:**
> "The AI knows the full context — the record, all exceptions, the upload. It can answer questions about impact, how to fix, or whether something is a false positive."

---

### 🎤 STEP 10: Dashboard (30 seconds)

**Do this:**
1. Click **Dashboard** in sidebar
2. Show the stat cards, quality score chart, exception breakdown

**Say this:**
> "The dashboard gives a real-time overview — total uploads, records, exceptions, resolution progress. At a glance, you know what needs attention."

---

### 🎤 STEP 11: Closing (30 seconds)

**Say this:**
> "To summarize, LoanVerify solves loan data verification with:
>
> 1. **Smart Ingestion** — Auto-detects 50+ column naming conventions
> 2. **CSV Preview** — See mappings before processing
> 3. **Validation Engine** — 13+ rules catching outliers and missing data
> 4. **AI Copilot** — Explanations + chat for follow-up questions
> 5. **Bulk Operations** — Resolve multiple exceptions at once
> 6. **Export** — Verified CSV, audit reports, hash manifests
> 7. **Hash Chain** — Tamper-evident audit trail
> 8. **Role-Based Access** — Analyst, Reviewer, Admin
>
> Built with React, FastAPI, SQLAlchemy, and OpenAI. Thank you — I'm happy to take questions."

---

## 📁 SAMPLE FILES TO USE

| Step | File | Location |
|------|------|----------|
| Step 3 | `clean_data.csv` | `backend/sample_data/clean_data.csv` |
| Step 4 | `messy_bank_export.csv` | `backend/sample_data/messy_bank_export.csv` |
| Step 6 | (use same upload from Step 4) | — |
| Step 7 | (export from Step 4 upload) | — |

---

## ❓ Q&A CHEAT SHEET

**Q: How does the hash chain work?**
> "Each record's SHA-256 hash includes the previous record's hash. Record 0 starts with 'GENESIS'. Tampering with any record breaks all subsequent hashes."

**Q: What if the AI gives wrong explanations?**
> "AI is advisory only. Reviewers must approve or dismiss. The AI also shows confidence levels."

**Q: How does this scale?**
> "Async FastAPI + SQLAlchemy. For production: PostgreSQL, Celery for background jobs, Redis for caching."

**Q: Can I customize validation rules?**
> "Yes — add a ValidationRule with a field, check function, and message. Takes 5 minutes."

**Q: What about data privacy?**
> "OpenAI is called only when reviewer requests explanation — no automatic upload. Could add data masking."

---

## 🎯 KEY POINTS TO EMPHASIZE

1. **"Not just an LLM wrapper"** — Real data engineering + AI assistance
2. **"Production-ready"** — Role-based auth, audit trail, hash chain
3. **"Demo-ready"** — Works with or without OpenAI API key
4. **"Follows the brief"** — Maps to all 6 problem statement requirements
5. **"Bulk operations"** — Real usability for reviewers

---

## ⚠️ BACKUP PLAN

If something fails during demo:
- **Upload fails:** Use the pre-uploaded data from previous test (refresh dashboard)
- **AI explanation fails:** Mock mode works without API key
- **Frontend crashes:** Reload page — all data is in the database
- **Server dies:** Run `uvicorn app.main:app --port 8000` again
