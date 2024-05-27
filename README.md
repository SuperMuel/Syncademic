# Syncademic

[Syncademic.io](https://syncademic.io) is a handy tool 🛠️ that makes it easy for you to manage your university schedule by syncing it directly with your Google Calendar 📅. Just give us the URL of your schedule, and we'll update your calendar automatically 🔄 whenever there are changes to your classes.

# Key Benefits of Syncademic

1. 📱 **Improved user experience**: Students use the familiar, multi-platform Google Calendar, avoiding clunky university tools.
2. 🌐 **Comprehensive view**: All academic, personal, and professional commitments are visible in one place for better planning and conflict avoidance.
3. 🔄 **Real-time updates**: Updates are frequent, ensuring students never miss important class changes. Updates triggered by one student benefit all users instantly.
4. 🖍️ **Customizable Experience**: You can personalize your calendar with color-coding and event title improvements to make it easier to read.
5. 🗓️ **Multi-schedule Management**: Ideal for students involved in multiple programs or institutions, Syncademic merges various academic schedules into a single Google Calendar view.

# Vocabulary used

- **User :** Someone using Syncademic to synchronize a time schedule. Mostly students but can be teachers
- **Time Schedule :** A structured list of academic events, such as lectures, seminars, and exams, organized in a calendar format.
- **Event :** One event of a Time Schedule or an electronic agenda. Has a start and end date, a title, description and location. Can optionally have a colour.
- **Time Schedule Source :** Identifies the source of a schedule, typically a URL from which schedule data can be imported or synchronized.
  - **Current Format Requirement:** The URL must specifically link to an .ICS file, which is typically hosted on institution servers, such as those of a school or university.
  - **Future Compatibility:** Plans are in place to support additional data sources for broader schedule integration capabilities.
- **Target Calendar :** The calendar where events from the Schedule Source are to be synchronized. Typically, a Google Calendar.
  - This does not define a Google Account, since users can have multiple calendars in the same Google Account. A target Calendar refers to a single Calendar in a user’s account.
- **Sync Profile** : (Synchronization Profile) Defines a user configuration for a synchronisation request between a **Time Schedule** and one **Target Calendar**
  - Users can have multiple Sync Profiles
- **Backend Authorization** : Refers to the permissions granted to Syncademic's backend by a user to access and modify one of their electronic agenda (such as a Google Calendar). It may include an access token and a refresh token, and may specify the scope of permitted actions. The status indicates whether access is granted or denied.
  - The Backend Authorization must last as long as the user is not deleting the Sync Profile. If the authorization is revoked, the user must be alerted.

## Frontend

The user interface (UI) for Syncademic is developed using Flutter.

**Goal**

- Authenticate users via Firebase Authentication with Google Sign-In.
- Allow users to input the URL of their time schedule.
- Enable users to select their Target Calendar for event synchronization.
- Authorize the backend to modify the user's calendar autonomously.

**Considerations**

- To select a Target Calendar, users complete an OAuth flow, which permits the frontend to display a list of their calendars and potentially create a new one for synchronization.
- Separate authorization processes are necessary for the frontend and backend: the frontend to display calendar options and the backend for calendar modifications. The frontend's authorization typically expires shortly after its use, as it's needed only for initial setup.

**UI/UX**

- The UI should simplify the synchronization process, guiding users step-by-step.
- Visual aids and graphics should illustrate how synchronization works, enhancing user understanding and interaction.

**Hosting**

- The Flutter application is compiled as a web app and hosted on Firebase Hosting.

**Mobile apps**

- The frontend is designed to be used infrequently. After the initial setup, the synchronization process should run automatically without needing any user input.
- Because of this, a hosted website would be sufficient for our requirements.
- However, we are also focusing on Android platforms. This is because developing on Android is simpler than web development, as Flutter's hot reload feature is available on Android but not on the web.

**Communication with the Backend**

- The app primarily interacts with Firebase Firestore for data operations.
- For actions like manually triggering synchronization, Cloud Function calls are used.

**Translation**

- The app is currently available in English. A translation library should be implemented to support additional languages, and appropriate translations provided.

## Backend

The backend is primarily built on Firebase Cloud Functions.

**Authentication**

- User authentication is managed through Firebase Auth.

**Database**

- Data storage and management are handled by Firebase Firestore (a NoSQL database).

**Synchronization Process**

- The backend continuously monitors SyncProfiles to ensure they are valid and initiates synchronization for each valid profile.
- A SyncProfile is deemed valid if the Schedule Source URL is correct and the backend has the necessary authorization to modify the Target Calendar.
- Synchronization is automatically triggered the first time a SyncProfile becomes valid, typically right after its creation.

**Authorization Handling**

- The backend is responsible for converting an Authorization Code into access tokens. (See OAuth section)

## Firebase Firestore Schema

### `users` collection

**Fields**

- `id` (string): Firebase Auth ID
- `email` (string): Email of the user, given by Firebase Auth

**Subcollections**

- `SyncProfiles` // Consider moving this to a root collection

  **Fields**

  - `title` (string)
  - `scheduleSource` (map)
    - `url` (string): URL that points to an ICS file
  - `status` (map)

    - `type` (string): The status type of the synchronization (`inProgress`, `failed`, `success`)
    - `message` (string): The error message if the synchronization failed
    - `syncTrigger` (string): The trigger of the synchronization (`on_create`, `manual`, `scheduled`)
    - `lastSuccessfulSync` (timestamp): The timestamp of the last successful synchronization

  - `targetCalendar` (map)
    - `id` (string): The ID of the target calendar
    - `title` (string): The title of the target calendar, given by the calendar provider.
    - `description` (string): The description of the target calendar, given by the calendar provider.
    - `providerAccountId` (string): This is the unique identifier for the account that owns the target calendar. It is not the same as the Firebase Auth ID used in our app. Currently, this ID represents a Google account, but in the future, it could also represent accounts from other providers like Microsoft. This distinction is important because a single user of our app can manage multiple synchronization profiles, each targeting calendars owned by different accounts across various providers.

### `backendAuthorizations` collection

Document ID: `userId` + `providerAccountId`

**Fields:**

- `userId` (string): The ID of the user who authorized the backend
- `providerAccountId` (string): The unique identifier of the authorized Google account
- `accessToken` (string): The access token obtained from the OAuth2 flow
- `refreshToken` (string): The refresh token obtained from the OAuth2 flow
- `expirationDate` (timestamp): The expiration date of the credentials

### Security Rules

Firestore security rules must be correctly defined in order to guarantee the safety of user data.

## Supported Electronic Agendas

**Current Support**

- Syncademic currently supports only Google Calendar. This integration is facilitated through the Google Calendar API v3, which allows efficient synchronization.

**Future Plans**

- We aim to extend support to a wider range of electronic agendas. Our goal is to accommodate as many target calendar platforms as possible, enhancing the versatility and reach of Syncademic.

# OAuth 2.0

OAuth 2.0 is a crucial protocol that enables secure authorization functionalities for our service, particularly in accessing users' Target Calendars.

**Overview**

- The backend requires authorization to access the user's Target Calendars for the duration that the SyncProfile is active.
- The frontend primarily facilitates the OAuth flow, allowing users to authorize access securely.

**Authorization Flow**

- We utilize the "Authorization Code" flow:
  - The frontend obtains an Authorization Code which is then sent to the backend via a function call.
  - The backend exchanges this code for an Access Token and a Refresh Token.
  - These tokens are subsequently stored in Firestore under the `backendAuthorizations` collection.

# Synchronization Process

The synchronization of events between a user's Time Schedule and their Target Calendar is a crucial functionality facilitated by the Google Calendar API v3. This process requires a valid access token.

### Synchronization Steps:

1. **Fetch Time Schedule Events:**
   - The process begins by attempting to fetch events from the Time Schedule. If events cannot be fetched, the synchronization is halted, and an error is communicated to the user, possibly through email or a mobile notification.
2. **Apply Customizations:**
   - Enhancements such as improving event titles or adding colors are applied to the events before synchronization.
3. **Update Target Calendar:**
   - All future events in the Target Calendar are deleted and replaced with the new, customized events.
   - To preserve the user’s personal events, only those created by Syncademic are deleted. This is achieved by marking each Syncademic event with the SyncProfile’s ID using Google Calendar's extended properties feature (`{"private": {"syncademic": sync_profile_id}}`).

### Deletion of a sync profile

There are multiple ways to handle the deletion of a sync profile.

1. **Keep everything**
   - The events created by Syncademic are kept in the target calendar. This is useful if the user wants to keep the events even after the sync profile is deleted.
2. **Delete events** <-- Default
   - When a sync profile is deleted, all events associated with it are deleted from the target calendar. This ensures that the user will not have to manually delete all events if they decide to stop this synchronization.
3. **Delete the whole calendar**
   - The target calendar is deleted when the sync profile is deleted. This is useful if the user wants to keep their main calendar clean and does not want to have a separate calendar for the events created by Syncademic.

### Current Limitations and Future Improvements:

- Currently, the system deletes and replaces all future events during each synchronization cycle, which is not the most efficient method.
- Moving forward, we aim to enhance efficiency by identifying and updating only those events that have changed, rather than replacing all events. This will optimize performance and reduce the load on both the server and the user's calendar.

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

**Current Implementation and Future Plans:**

- Currently, customization rules are hardcoded into the backend.
- Moving forward, we aim to empower users by allowing them to choose or define their own customization rules. This flexibility will enable users to tailor their calendars to better meet their personal needs and preferences.
