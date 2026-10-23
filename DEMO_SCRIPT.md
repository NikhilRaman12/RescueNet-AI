# ReadyAtHome demo script · target 2:40

Record the actual local application in a browser. Keep the video under three minutes, in English, and publish it on YouTube or Vimeo. Do not add simulated device connections, live data, or unrecorded results.

## Before recording

- Start the API and Vite as described in README.md; use `USE_LIVE_APIS=false`.
- Open `http://127.0.0.1:5173/ready-at-home.html`.
- Use the visible sample request. Do not show terminal variables, secrets, local database files, or personal data.
- If using an existing task history, show it as local activity rather than a new-session result. **New rehearsal** resets browser flags but intentionally keeps that history.

## Timed walkthrough

### 0:00–0:15 · The promise

**Say:** “ReadyAtHome turns one household-preparedness question into a clear, explainable plan. This is an independent Alexa+ interaction simulation.”

**Show:** Product heading, simulation badge, and typed input.

### 0:15–0:40 · Generate the plan

**Say:** “I’ll ask for help preparing for possible flooding. The app accepts flood and heavy-rain preparation requests; its rules choose a fixed checklist.”

**Show:** Submit the sample and point to the U.S. guidance label, planning-scenario summary, and completed/remaining count.

### 0:40–1:15 · Explain the steps and sources

**Say:** “Each step explains what to do, why it appears, and the reference behind it. These are U.S. government guidance links, not live information fetched by this app.”

**Show:** Expand a task explanation and show its source link. Keep the assumptions and no-live-alert status visible.

### 1:15–1:45 · Complete and reopen a task

**Say:** “I can complete and reopen a step. Progress updates, and the local backend records the action and time without storing the request text.”

**Show:** Check and uncheck a task; point to the updated progress and newest activity event.

### 1:45–2:10 · Recover safely from unsupported and urgent input

**Say:** “A hurricane request is outside the supported scope, so the app does not return a misleading flood plan. If a request suggests immediate danger, it points people to local emergency services instead of showing a routine checklist.”

**Show:** Enter “Help me prepare for a hurricane,” submit, then try “My house is flooding right now.” Show each recovery message and leave the text visible.

### 2:10–2:30 · Reset without deleting history

**Say:** “New rehearsal clears this browser’s checklist marks. The SQLite activity history remains available when I generate the plan again.”

**Show:** Generate the supported plan again if needed, complete one task, choose **New rehearsal**, then generate the plan and show retained activity.

### 2:30–2:40 · Close with the boundary

**Say:** “There is no microphone, Alexa connection, live alert, evacuation route, or shelter data. Follow current local authorities in a real emergency.”

**Show:** End on the simulation label and safety footer.

## Evidence checklist

- Capture real footage of the sequence above and verify the final runtime is under three minutes.
- Do not describe this as a hardware or official Alexa+ integration.
- Screenshots to capture from the real app: initial request and simulation label; generated plan with U.S. guidance and task rationale; a completed task with recent activity; unsupported-input recovery; reset message and safety footer.
- No screenshot is currently included. The browser automation surface was unavailable during this verification run, so capture from a working browser before submission.
- Publish the actual video and add its verified URL to the submission; no video URL is prepared yet.
