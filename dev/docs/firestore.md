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
  - `ruleset` (string): A valid JSON string a Ruleset to apply.

### `backendAuthorizations` collection

Document ID: `userId` + `providerAccountId`

**Fields:**

- `userId` (string): The ID of the user who authorized the backend
- `provider` (string): The provider of the authorized account. For now, it is always `google`
- `providerAccountId` (string): The unique identifier of the authorized Google account
- `providerAccountEmail` (string): The email of the authorized Google account
- `accessToken` (string): The access token obtained from the OAuth2 flow
- `refreshToken` (string): The refresh token obtained from the OAuth2 flow
- `expirationDate` (timestamp): The expiration date of the credentials