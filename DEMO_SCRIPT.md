# ReadyAtHome demo script · target 2:40

**Recording requirement:** capture the real application running in a browser. Do not add simulated metrics, a fake device connection, or unrecorded results. Keep the final video under three minutes, publish it in English on YouTube or Vimeo, and show the new ReadyAtHome interaction.

## Before recording

- Start FastAPI from the repository root with USE_LIVE_APIS=false.
- Start Vite in frontend and open http://127.0.0.1:5173/ready-at-home.html.
- Keep the browser on the ReadyAtHome page and clear only unrelated browser tabs from view.
- Do not show terminal environment variables, secrets, private data, or the ignored local database.
- Use the sample utterance already shown in the page.

## Timed narration

### 0:00–0:15 · Introduce the product

**Say:** “ReadyAtHome turns a household preparedness request into a short, explainable plan. This is an independent Alexa+ interaction simulation for the Amazon Developer Hackathon.”

**Show:** ReadyAtHome title and the visible simulation badge.

### 0:15–0:35 · Start the reproducible request

**Say:** “I’ll ask for help preparing for possible flooding. The text simulates a voice request; this browser has no microphone or Alexa connection.”

**Show:** Submit the sample request and wait for the response card.

### 0:35–1:00 · Explain the assessment

**Say:** “The local rules choose a flood-preparedness checklist. This is a planning scenario, not a forecast. It did not check my location or current alerts.”

**Show:** Scenario label, assumptions, rationale, and the ‘not connected’ weather/alerts status.

### 1:00–1:40 · Inspect the checklist

**Say:** “The first step is to check official local alerts. I can open the reason for each suggestion and see the FEMA, Ready.gov, or National Weather Service reference behind it.”

**Show:** Open a task’s explanation, then point to the official source links without implying that the app fetched them.

### 1:40–2:05 · Record a task

**Say:** “I’ll mark the official-alert check complete. The checklist progress changes, and the local audit view records only the task ID and time.”

**Show:** Check the task and show the activity item.

### 2:05–2:25 · State the boundaries

**Say:** “Weather, evacuation orders, routes, shelter availability, speech recognition, and Amazon services are not connected. The request text is not stored.”

**Show:** Integration status and safety footer.

### 2:25–2:40 · Close

**Say:** “ReadyAtHome helps rehearse preparedness steps. During an emergency, follow official local alerts and emergency services.”

**Show:** End on the full page with the prototype notice visible.

## Reproducible demo flow

1. Type the sample flood-preparedness request and submit it.
2. Read the planning-scenario status and assumptions.
3. Expand one “Why this is on the list” detail.
4. Mark one checklist item complete.
5. Show the matching recent-activity event.
6. Show simulation and not-connected labels plus the safety notice.

## Evidence still needed

- Record the actual browser journey described above.
- Take real screenshots of the initial ReadyAtHome page, generated plan and rationale, task completion with audit event, and integration/safety labels.
- Publish the video publicly on YouTube or Vimeo and add its URL to the submission.
- Do not fabricate device access, alerts, user feedback, deployment, or judging evidence.
