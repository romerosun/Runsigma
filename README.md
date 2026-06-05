# Motion-Based Labor Scheduling Demo

A Streamlit app that explains how a company can build schedules from MOST-style motion labor estimates instead of only using sales-per-labor-hour targets.

## What it shows

- Avatar-style motion breakdown: reach, grasp, move, place, walk, scan
- Fixed task time plus allowance
- Labor time build-up chart
- Sales-based schedule vs motion-based schedule
- Staffing rules and schedule allocation from employee availability

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repo.
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Go to Streamlit Community Cloud.
4. Select the repo.
5. Set the main file path to `app.py`.
6. Deploy.

## Suggested positioning

We do not just schedule from sales or historical averages. We model the work itself. The algorithm estimates labor from the motions required to complete each task, adds realistic allowances, converts the work into staffing rules, and builds a schedule managers can adjust.
