# Concepts in Syncademic

## Vocabulary

### User

An individual who uses Syncademic to synchronize their academic schedule with their Google Calendar. Users will mostly be students but can also include teachers or other academic professionals.

### Time Schedule

A structured list of academic events, such as lectures, seminars, and exams, organized in a calendar format.

### Event

An individual entry in a time schedule or calendar application. Events have a start and end time, a title, a description, a location, and an optional color.

### Time Schedule Source

The origin of the time schedule data. Currently, the only source supported is an URL to an `.ICS` file. The file will typically be hosted on the user's educational institution servers. 

### Target Calendar

The calendar where events from the time schedule are synchronized. Currently, **only Google Calendar is supported**. 
A target Calendar is **not** a Google Account, since a user can have multiple calendars within their Google Account (e.g., personal, work, school).
A target Calendar is a reference to a specific calendar within a Google Account.

- **Provder**: The calendar provider (Currently only Google).
- **Calendar ID**: The unique identifier for the calendar within the provider's system.
- **Provider Account ID**: The unique identifier for the user's account within the provider system.


### Sync Profile

A configuration that specifies:

- **Time Schedule Source**: The `.ICS` URL to sync from.
- **Target Calendar**: The calendar to sync events to.
- **Customization Rules**: Rules to modify events during synchronization. Currently, these rules are AI generated and not editable.
- **Status**: Indicates if synchronization is successful, in progress, or failed.
- **Title**: A user-defined name for the profile.

Users can have multiple sync profiles.

### Backend Authorization

Permissions granted to Syncademic's backend to access and modify a user's target calendar. Involves:

- **OAuth 2.0 Tokens**: Access and refresh tokens.
- **Expiration Time**: Tokens are valid for a limited period.
- **Provider**: The calendar provider (e.g., Google).
- **Provider Account ID**: Unique identifier for the user's account.


### Customization Rules

Instructions that specify how events should be modified. 

- **Conditions**: Criteria based on event attributes (title, description, etc.).
- **Actions**: Modifications like changing titles, colors, or deleting events.

### Time Schedule Compression

The process of summarizing time schedule data before feeding it to the AI model.

- **Fit Context Limitations**: LLMs have a maximum input size.
- **Provide Essential Information**: Include representative samples and patterns.
- **Enhance AI Performance**: Focus on relevant data for rule generation.

### Event Clustering

Grouping similar events during compression. Purpose:

- **Identify Patterns**: Helps in recognizing common event types.
- **Simplify Data**: Makes the schedule manageable for AI processing.
- **Representative Samples**: Provides context without overwhelming detail.

# Synchronization Process

## Synchronization Steps:

1. **Fetch Time Schedule Events:**
   - The process begins by attempting to fetch events from the Time Schedule. If events cannot be fetched or the file is too large, the synchronization is halted, and an error is stored in the syncProfile status.
2. **Parse the ICS file**
    - The fetched ICS file is parsed to extract event details. If the time schedule is empty, the synchronization stops successfully.
2. **Apply Customizations:**
   - If the syncProfile contains customization rules, they are applied to the events fetched from the Time Schedule. If this steps deletes all events, the synchronization stops successfully.
3. **Update Target Calendar:**
   - This steps involves updating the Target Calendar with the modified events.
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

## Types of synchronizations

### Initial Synchronization
Before the first synchronization, customization rules are automatically created with AI. This is currently not editable by the user, and cannot be revised.
On the first synchronization, all events from the time schedule are added to the target calendar, even if they are in the past.

### Regular Synchronization
After the initial synchronization, the system only updates events that have changed in the time schedule. (Currently, this is all future events, as we do not have a change detection mechanism in place yet.)

### Full Synchronization
In case the user wants to update all events in the target calendar, they can trigger a full synchronization. This will delete all events created by Syncademic and add all events from the time schedule. This is useful if the user has made accidental changes to the events, or in case of errors in the synchronization process.

## Current Limitations and Future Improvements:

### Bruteforce Event Replacement
Currently, the system deletes and replaces all future events during each synchronization cycle, which is not the most efficient method.
This is temporary because we need to first implement a method to detect changes in the time schedule and only update the events that have changed.
But implementing this change-detection is not trivial because a lot of time schedules do not have unique identifiers for each event, and they contain some dynamic data that changes every time the schedule is fetched.

