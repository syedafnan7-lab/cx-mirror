# CX MIRROR

> **"Your Design. Your Experience. Mathematically Verified."**  
> *HackStellar PS-18: AI Testing Against Design Mockups*  
> *Built on Google Antigravity v2.28+*

---

## 1. Executive Summary

CX Mirror is a deterministic, multi-modal visual QA and experience verification platform. Traditional pixel-comparison algorithms produce catastrophic false positives when dynamic customer data changes (dates, user greetings, inventory countdowns, promotional prices). Conversely, pure Vision-LLMs hallucinate bounding box coordinates, fail at sub-pixel geometry, and cannot compute exact colorimetric Delta E or WCAG contrast ratios.

CX Mirror solves this via a hybrid mathematical pipeline:
1. **Live DOM Spatial Graph ($G_D$):** Extracted via Playwright CDP (`getBoundingClientRect()` and `window.getComputedStyle()`) under strict reproducible rendering conditions (`rendering_config.json`).
2. **Mockup Spatial Graph ($G_M$):** Extracted via OpenCV contour hierarchy, morphological operators, and color sampling.
3. **Multi-Modal Hungarian Assignment:** Solved via `scipy.optimize.linear_sum_assignment` combining Complete IoU (CIoU), windowed SSIM, CIE L\*a\*b\* Delta E, and Unicode token similarity.
4. **Statutory Reference Data Contracts:** Enforcing exact SKU pricing, statutory legal disclaimer legibility, and WCAG AA contrast (4.5:1).
5. **Interactive Forensic Workbench:** Dark-mode React dashboard featuring interactive SVG displacement laser vectors, split-screen wipe comparison, real-time threshold slider, and an empirical 60-scenario ROC benchmark lab.

---

## 2. Mathematical Foundations

### Complete Intersection-over-Union (CIoU)
$$\text{IoU} = \frac{|A \cap B|}{|A \cup B|}$$
$$\text{CIoU} = \text{IoU} - \frac{\rho^2(b_A, b_B)}{c^2} - \alpha v$$
where $\rho$ is the Euclidean center distance, $c$ is the enclosing diagonal, and $v$ penalizes aspect-ratio deviation:
$$v = \frac{4}{\pi^2} \left( \arctan\frac{w_B}{h_B} - \arctan\frac{w_A}{h_A} \right)^2, \quad \alpha = \frac{v}{(1 - \text{IoU}) + v + \epsilon}$$
Normalized cost: $C_{\text{geometry}} = \frac{1 - \text{clamp}(\text{CIoU}, -1, 1)}{2} \in [0, 1]$.

### Structural Similarity (SSIM)
$$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$
Normalized cost: $C_{\text{ssim}} = \frac{1 - \text{clamp}(\text{SSIM}, -1, 1)}{2} \in [0, 1]$.

### Perceptual Color Difference (CIE L\*a\*b\* $\Delta E_{ab}^*$)
sRGB channels are companded to linear space and mapped to CIE XYZ with D65 illuminant, then converted to CIE L\*a\*b\*:
$$\Delta E_{ab}^* = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}, \quad C_{\text{color}} = \min\left(\frac{\Delta E_{ab}^*}{100}, 1.0\right)$$

### Multi-Modal Cost Matrix & Hungarian Assignment
$$C[i, j] = 0.35 C_{\text{geometry}} + 0.20 C_{\text{ssim}} + 0.15 C_{\text{color}} + 0.30 C_{\text{text}} + P_{\text{semantic}}$$
Assignments are solved using `scipy.optimize.linear_sum_assignment` with dummy node thresholds ($0.75$) and semantic role incompatibility penalties ($P_{\text{semantic}} \in [0.0, 0.90]$).

### Confidence Scoring & Verdict
$$Q_i = 1 - (w_g C_{\text{geometry}} + w_s C_{\text{ssim}} + w_c C_{\text{color}} + w_t C_{\text{text}})$$
$$S_{\text{visual}} = 100 \times \frac{\sum a_i Q_i}{\sum a_i}, \quad S_{\text{structure}} = 100 \times (1 - \text{Penalty}_{\text{structural}}), \quad S_{\text{contract}} = 100 \times \frac{\text{Passed}}{\text{Total}}$$
$$S_{\text{total}} = 0.60 S_{\text{visual}} + 0.15 S_{\text{structure}} + 0.25 S_{\text{contract}}$$

**Verdict Rule:**
$$\text{Verdict} = \text{PASS} \iff S_{\text{total}} \ge \tau \text{ (default 95.0) } \land \text{Critical Failures} = 0$$

---

## 3. Quickstart & Installation

### Requirements
- Python 3.10+ (Tested on 3.12.10)
- Node.js 18+ (Tested on v24.18.0)
- npm 9+

### Option A: Windows Automated Bootstrap
```powershell
# From the repository root:
.\scripts\bootstrap.ps1
```

### Option B: Manual Startup

1. **Activate Python Virtual Environment & Install Dependencies:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m playwright install chromium
```

2. **Generate Baseline Golden Mockup:**
```powershell
python scripts/generate_golden.py
```

3. **Install Frontend Dependencies & Build:**
```powershell
cd frontend
npm install
npm run build
cd ..
```

4. **Launch Backend Server (Port 8000):**
```powershell
.\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

5. **Launch Frontend Dev Server (Port 5173):**
```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open your browser to: **`http://localhost:5173`**

---

## 4. REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/analyze` | Multipart analysis with mockup upload or golden baseline |
| `GET` | `/api/analysis/{id}` | Retrieve cached verification report |
| `GET` | `/api/presets` | List all 5 sandbox mutation presets |
| `GET` | `/api/presets/{name}` | Inspect specific preset details and defects |
| `GET` | `/api/roc-benchmark` | Execute empirical 60-scenario ROC comparison (Seed 42) |
| `GET` | `/api/reference-data` | Retrieve active business data contracts |
| `GET` | `/api/health` | Service uptime and version health check |
| `GET` | `/api/artifacts/{name}` | Safely stream screenshot evidence and artifacts |
| `GET` | `/sandbox?preset={name}` | E-commerce checkout sandbox (`clean`, `drifted`, `price_bug`, `legal_hidden`, `all_bugs`) |

---

## 5. 30-Second Judge Demonstration Sequence

| Step | Preset | Key Customer Experience Difference | Expected Verdict | Confidence |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `clean` | Golden baseline matching authorized $24.99 SKU contract | **PASS** | **100.0%** |
| **2** | `price_bug` | Live checkout charges $19.99 (violates $24.99 business contract) | **CRITICAL FAIL** | **94.53%** (Contract Override) |
| **3** | `legal_hidden` | Mandatory legal disclaimer rendered at 5px with 0.05 opacity (WCAG 1.1:1) | **CRITICAL FAIL** | **87.08%** (Legal Override) |
| **4** | `drifted` | Layout shifted +28px, CTA button changed to Purple (#9333EA) | **FAIL** | **87.68%** (22 Discrepancies) |
| **5** | **Lab** | 60-Scenario ROC Benchmark: CX Mirror AUC 1.000 vs Pixel Diff 0.318 | **LAB PROOF** | Empirical Superiority |

---

## 6. Verification Artifacts & Screenshots

Screenshots captured directly by Chromium automation in `artifacts/screenshots/`:
- `01_clean_pass.png`: Clean baseline passing all contracts (100.0% confidence)
- `02_drifted_lasers.png`: Drifted layout showing interactive SVG displacement laser vectors
- `03_split_screen_wipe.png`: Split-screen wipe slider comparing golden mockup and live implementation
- `04_price_bug_fail.png`: Critical contract failure highlighting SKU pricing mismatch
- `05_legal_hidden_fail.png`: Critical legal failure highlighting hidden 5px disclaimer
- `06_all_bugs_fail.png`: Compounded regressions and simultaneous contract violations
- `07_benchmark_lab_roc.png`: Recharts comparative ROC curves and confusion matrix
- `08_executive_dashboard.png`: Dark forensic dashboard overview and KPI metrics
- `09_reference_contracts.png`: Business data contracts and WCAG accessibility standards

---

## 7. License & Credits
CX Mirror is built for HackStellar PS-18 on Google Antigravity v2.28+.
"Your Design. Your Experience. Mathematically Verified."

