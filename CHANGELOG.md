## 08:38

### Features Added
- Initialized template with AGENTS.md, CHANGELOG.md, and base structure

### Files Modified
- AGENTS.md
- CHANGELOG.md
- progress/.gitkeep

### Issues Faced
- None

## 12:49

### Features Added
- Added final changes to template, including local template image assets
- Refactored AGENTS.md, README.md, and CHANGELOG.md forms

### Files Modified
- AGENTS.md
- CHANGELOG.md
- README.md
- template_acm.png
- template_clique.png

### Issues Faced
- Initial remote image download attempt failed, resolved by using provided local files

## 17:48

### Features Added
- First actual commit updating README for core repository

### Files Modified
- README.md

### Issues Faced
- None

## 18:02

### Features Added
- Created foundational project structure for Insidra backend and models

### Files Modified
- Insidra/app.py
- Insidra/backend/pipeline.py
- Insidra/backend/risk_engine.py
- Insidra/backend/utils.py
- Insidra/data/logs.csv
- Insidra/model/anomaly_model.py

### Issues Faced
- None

## 18:19

### Features Added
- Added Python requirements file and fleshed out core pipeline logic

### Files Modified
- Insidra/backend/pipeline.py
- Insidra/requirements.txt

### Issues Faced
- None

## 19:12

### Features Added
- Generated initial synthetic dataset and data generation script

### Files Modified
- Insidra/data/logs.csv
- Insidra/data_gen.py

### Issues Faced
- None

## 19:26

### Features Added
- Refactored pipeline architecture and dataset to strictly align with System Spec
- Added preprocessing and risk engine logic

### Files Modified
- Insidra/app.py
- Insidra/data/logs.csv
- Insidra/data/scored_logs.csv
- Insidra/data_gen.py
- Insidra/model/anomaly_model.py
- Insidra/model/preprocess.py
- Insidra/model/risk_engine.py
- progress/1.csv

### Issues Faced
- None

## 19:36

### Features Added
- Built interactive Streamlit Dashboard to visualize behavioral drift and fulfill Demo Story

### Files Modified
- Insidra/data/logs.csv
- Insidra/data/scored_logs.csv
- dashboard.py
- progress/2.webp

### Issues Faced
- None

## 20:12

### Features Added
- Consolidated backend code structure into `Insidra/` directory
- Integrated dashboard component into main Insidra module
- Updated synthetic data pipelines

### Files Modified
- Insidra/backend/pipeline.py
- Insidra/dashboard.py
- Insidra/data/logs.csv
- Insidra/data/scored_logs.csv
- dashboard.py
- walkthrough.md

### Issues Faced
- None

## 00:52

### Features Added
- Fixed bug where `stream_generator.py` unconditionally assigned all events to U5 after step 20
- Expanded the simulated ecosystem from 5 to 10 users, adding U6, U7, U8, U9, and U10
- Introduced two new malicious actors (U9 and U10) to the risk evolution simulations alongside U5
- Regenerated synthetic `logs.csv`

### Files Modified
- Insidra/data_gen.py
- Insidra/stream_generator.py
- Insidra/data/logs.csv

### Issues Faced
- None
