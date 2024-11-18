# Syncademic

[Syncademic.io](https://syncademic.io) is a handy tool 🛠️ that makes it easy for you to manage your university schedule by syncing it directly with your Google Calendar 📅. Just give us the URL of your schedule, and we'll update your calendar automatically 🔄 whenever there are changes to your classes.

![Diagram of Syncademic](images/diagram_exalidraw.png)

![Screenshots of Syncademic](images/app_screens.jpg)

<script src="https://cdn.commoninja.com/sdk/latest/commonninja.js" defer></script>
<div class="commonninja_component pid-cdab97f0-73e8-4b81-b367-b07afff6dd21"></div>


# Key Benefits of Syncademic

1. 📱 **Improved user experience**: Students use the familiar, multi-platform Google Calendar, avoiding clunky university tools.
2. 🌐 **Comprehensive view**: All academic, personal, and professional commitments are visible in one place for better planning and conflict avoidance.
3. 🔄 **Real-time updates**: Updates are frequent, ensuring students never miss important class changes. Updates triggered by one student benefit all users instantly.
4. 🖍️ **Customizable Experience**: You can personalize your calendar with color-coding and event title improvements to make it easier to read.

# 🚀 How It Works

Use the app at [app.syncademic.io](https://app.syncademic.io) to setup your synchronization. Once you're done, you don't need the app anymore ! Just open your Google Calendar and enjoy your beautiful, updated schedule.

1. **Input Your Schedule**:
   - Provide a URL to your academic schedule. This URL is typically provided by your university.
2. **AI Customization**:
   - AI processes your schedule, cleaning up titles, adding colors, and removing irrelevant entries if needed.
3. **Sync to Google Calendar**:
   - Your customized schedule is seamlessly synced to your Google Calendar.


# Customization

The primary goal of Syncademic is to enhance the visual appeal of time schedules for students and teachers. Traditional time schedules often lack color and can have cryptic titles, making them hard to understand and visually unattractive.

**Problem Statement:**

- Common time schedules may use opaque identifiers like `HU-L-S1-CMP-ANG-4--ING:TD` instead of more descriptive and straightforward titles such as `Anglais TD`.
- These schedules typically do not utilize colors, which can help in distinguishing different types of events at a glance.

**Syncademic Customizations:**
To address these issues, Syncademic applies customization rules to events between fetching the TimeSchedule and updating the Target Calendar:

**Examples of Customization Rules:**

1. **Color Coding:**
   - `If "Machine Learning" is in the description, then make the event blue.`
   - This rule enhances the visual appeal and helps students quickly identify specific classes.
2. **Event Filtering:**
   - `If "Anglais" is in the description, then delete the event.`
   - Useful for users who want to exclude irrelevant courses automatically included in their schedules.
3. **Title Enhancement:**
   - `Find the text between '[' and ']' in the description and place that in the title.`
   - Improves event titles by extracting and using more descriptive text found within the event details.