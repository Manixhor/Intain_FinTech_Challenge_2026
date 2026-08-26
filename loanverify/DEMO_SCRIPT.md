# 🎬 LoanVerify — Demo Script
## Intain FinTech Challenge 2026 — Full Stack Track

**Duration:** 8-10 minutes
**Presenter:** Your name here
**Setup:** Backend on localhost:8000, Frontend on localhost:3000

---

## 🎯 Opening (30 seconds)

> "Hi, I'm [Your Name]. Today I'll demo **LoanVerify** — an AI-powered Loan Data Verification Copilot.
>
> The problem: Financial institutions receive messy loan data from multiple sources — CSV exports, spreadsheets, APIs. This data has errors, outliers, and inconsistencies. Currently, humans manually review every row, which is slow and error-prone.
>
> Our solution: Upload a messy loan tape, and LoanVerify automatically normalizes it, validates it, explains issues with AI, and creates a tamper-evident audit trail. Let me show you."

---

## 📋 Step 1: Login & Role-Based Access (1 minute)

**Action:** Open http://localhost:3000

**Say:**
> "We have three user roles — Analyst, Reviewer, and Admin. Each role has different permissions."

**Action:**
1. Show the login page
2. Click the **analyst** demo button
3. Click **Sign In**

**Say:**
> "As an Analyst, I can upload files and view my own data, but I cannot resolve exceptions — that's a Reviewer's job."

**Action:** Show the sidebar with the user role badge (blue "analyst" badge)

---

## 📤 Step 2: Upload a Clean File (1.5 minutes)

**Action:** Click **Upload Data** in sidebar

**Say:**
> "Let me first upload a clean dataset to show the baseline."

**Action:**
1. Drag `clean_data.csv` onto the upload zone (or click to browse)
2. Wait for processing (~2 seconds)

**Say:**
> "20 records processed. Quality score: 98 out of 100. Only 7 minor issues detected."

**Action:** Click **View Details & Exceptions**

**Say:**
> "The system auto-detected 13 columns from the CSV header and mapped them to our standard schema. Each record got a SHA-256 hash, and they're chained together for tamper evidence."

**Action:**
1. Show the exceptions tab (7 warnings)
2. Click on a few exception cards to show the details
3. Show the "Expected" vs "Actual" values

---

## 📤 Step 3: Upload a Messy File (2 minutes)

**Action:** Go back to **Upload Data**

**Say:**
> "Now let's upload a realistic bank export. Notice the column names are completely different — `Acct #` instead of `loan_id`, `APR %` instead of `interest_rate`, `Disb Date` instead of `origination_date`."

**Action:**
1. Upload `messy_bank_export.csv`
2. Wait for processing

**Say:**
> "35 records processed. Quality score: [score]. The system automatically detected that `Acct #` maps to `loan_id`, `Borrower Full Name` maps to `borrower_name`, and so on — even with different naming conventions."

**Action:** Click **View Details & Exceptions**

**Action:**
1. Show the Records tab — scroll through the normalized data
2. Point out the clean, consistent column names
3. Show that `Acct #` became `loan_id`, `APR %` became `interest_rate`

---

## 🤖 Step 4: AI Explanation (2 minutes)

**Action:** Go to Exceptions tab

**Say:**
> "Now here's where AI comes in. Every exception gets an explanation from our AI copilot."

**Action:**
1. Find the exception for row with 45% interest rate (critical)
2. Click **Explain** button

**Say:**
> "The AI explains: 'The interest rate of 45% is outside the typical range of 0.1% to 30%. This could indicate a data entry error — perhaps a missing decimal point. Verify with the source system.' This saves the reviewer hours of manual investigation."

**Action:**
1. Show the AI explanation card (purple background)
2. Find another exception (missing borrower name) and explain it too
3. Show the batch explanation feature if time allows

**Say:**
> "The AI also suggests fixes — like checking the source data for the correct value."

---

## 🔗 Step 5: Hash Chain & Audit Trail (1.5 minutes)

**Action:** Click **Audit & Hash Chain** tab

**Say:**
> "Every record in the system is cryptographically linked. Let me show you."

**Action:**
1. Click **Verify Chain** button
2. Show the green "Chain Integrity Verified ✓" message

**Say:**
> "All 35 records are verified. Each record's hash depends on the previous record's hash — just like a blockchain, but without the infrastructure overhead. If anyone tampers with even one record, the entire chain breaks."

**Action:**
1. Show the Audit Log entries below
2. Point out the timestamped actions: "file_uploaded", "file_processed", "ai_explanation_generated"

**Say:**
> "Every action is logged — who did what, when. This creates a complete audit trail for compliance."

---

## 👥 Step 6: Role-Based Workflow (1 minute)

**Action:** Click the user icon in sidebar → **Log Out**

**Say:**
> "Now let me switch to a Reviewer role to show the exception resolution workflow."

**Action:**
1. Login as **reviewer** / demo123
2. Go to the upload detail page
3. Show that the Resolve and Dismiss buttons are now visible

**Say:**
> "As a Reviewer, I can now resolve or dismiss exceptions. An Analyst cannot do this — only Reviewers and Admins."

**Action:**
1. Click **Resolve** on one exception
2. Show the status change to "resolved"
3. Show the dashboard updated

**Say:**
> "The resolution is logged in the audit trail with my username and timestamp."

---

## 📊 Step 7: Dashboard (1 minute)

**Action:** Click **Dashboard** in sidebar

**Say:**
> "The dashboard gives a real-time overview of all verification activity."

**Action:**
1. Show the stat cards: Total Uploads, Total Records, Exceptions, Resolved
2. Show the Quality Score circle chart
3. Show the Exception Breakdown bars (Critical / Warning / Info)
4. Show the Recent Uploads list
5. Show the Resolution Progress bar

**Say:**
> "At a glance, you can see data quality across all uploads, how many issues have been resolved, and which uploads need attention."

---

## 🎯 Step 8: Stress Test (1 minute)

**Action:** Upload `large_dataset.csv` (100 records)

**Say:**
> "Let me upload a larger dataset to show performance."

**Action:**
1. Upload the file
2. Show it processes quickly
3. Show the Records tab with pagination
4. Show 100 records paginated 15 per page

**Say:**
> "100 records processed in under 2 seconds. The Records tab shows pagination for easy browsing."

---

## 🏁 Closing (30 seconds)

**Say:**
> "To summarize, LoanVerify solves the loan data verification problem with:
>
> 1. **Smart Ingestion** — Auto-detects column mappings from 50+ naming conventions
> 2. **Validation Engine** — 13+ rules catching outliers, missing fields, invalid data
> 3. **AI Copilot** — GPT-powered explanations in plain English
> 4. **Hash Chain** — Tamper-evident audit trail without blockchain infrastructure
> 5. **Role-Based Access** — Analyst, Reviewer, Admin with appropriate permissions
>
> Built with React, FastAPI, SQLAlchemy, and OpenAI. Ready for production deployment.
>
> Thank you. I'm happy to take questions."

---

## ❓ Anticipated Q&A

**Q: How does the hash chain work?**
> "Each record computes a SHA-256 hash from its data plus the previous record's hash. Record 0 starts with 'GENESIS'. This creates a chain where tampering with any record breaks all subsequent hashes — exactly like a blockchain, but implemented in pure Python with no external infrastructure."

**Q: What happens if the AI gives a wrong explanation?**
> "The AI explanation is advisory — it doesn't auto-resolve. A human Reviewer must always approve or dismiss. The AI also shows its confidence level, and reviewers can override."

**Q: How does this scale?**
> "The backend is async FastAPI with SQLAlchemy. For production, we'd swap SQLite for PostgreSQL, add Celery for background processing, and use Redis for caching. The validation engine is parallelizable."

**Q: What about data privacy?**
> "The OpenAI API is called only when a reviewer requests an explanation — no automatic data upload. We could add data masking before sending to external APIs. All data stays in the local database."

**Q: Can I customize the validation rules?**
> "Yes, the validation engine is rule-based and extensible. Adding a new rule is just adding a ValidationRule object with a field, check function, and message."

---

## 📁 Files to Have Open During Demo

1. **Browser:** http://localhost:3000 (the app)
2. **Terminal:** Backend running on port 8000
3. **Sample data folder:** `backend/sample_data/` ready to drag-and-drop

## ⏱️ Timing Summary

| Section | Duration |
|---------|----------|
| Opening | 0:30 |
| Login & Roles | 1:00 |
| Clean File Upload | 1:30 |
| Messy File Upload | 2:00 |
| AI Explanation | 2:00 |
| Hash Chain & Audit | 1:30 |
| Role Workflow | 1:00 |
| Dashboard | 1:00 |
| Stress Test | 1:00 |
| Closing | 0:30 |
| **Total** | **~12 min** |

**For a 8-min presentation, skip Steps 7 (Dashboard) and 8 (Stress Test).**
