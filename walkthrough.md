# Insidra: The Complete Package

The system is fully built, passing all checks, and the final Streamlit Dashboard brings the entire backend pipeline to life.

## 🎯 The Demo Story Fulfillment

The dashboard is designed specifically to execute the 4 key steps of your narrative effortlessly:

1. **Show normal user → low risk:** By using the sidebar, you can select standard users (e.g. `U1`, `U3`). You will see their risk scores float harmlessly in the 0-15 range and their status remain `LOW`.
2. **Show gradual drift → increasing risk:** Switching the selector to `U5` (which the UI flags as `🔴 U5 (HIGH RISK)` automatically) will display the Plotly line chart. It clearly maps out the timeline where the score starts creeping into the yellow `MEDIUM RISK ZONE` (40-70).
3. **Show final spike → HIGH alert:** Towards the end of the timeline, you will see a massive spike vaulting the risk score to `100`, definitively plunging into the red `HIGH RISK ZONE`.
4. **Explain WHY flagged:** Immediately below the graph, a dynamically colored table lists every single anomaly threshold crossed, fully contextualizing the score jump with raw reasoning (e.g. `"Spike in file access, Access from new location"`). 

## 🎬 Verification Recording

Watch the automated agent visually verify the `U5` threat detection below:

![Dashboard Verification Demonstration](file:///C:/Users/mahin/.gemini/antigravity/brain/d46b8e48-1fbf-4dfb-995a-31993143b9a9/dashboard_verification_1774620221771.webp)

## 🛡️ Hackathon Final Check
- ✅ The entire application runs natively. The dynamic visualization perfectly masks the complex behavioral modeling processing underneath.
- ✅ The latest verifiable video recording has been captured and submitted to `progress/2.webp`.
- ✅ An official git commit tracking the dashboard build has been deployed.
