## Firebase Firestore Schema

### `users` collection

**ID**: Firebase Auth ID.

**Fields**

- `email` (string, optional): Email of the user. (Currently unsecured as it's provided by the frontend. Use data in FirebaseAuth instead.)

**Subcollections**

- #### `syncProfiles`

  **Fields**

  - `title` (string)
  - `scheduleSource` (map)
    - `url` (string): URL pointing to an ICS file.
  - `status` (map)
    - `type` (string): The status type of the synchronization (`inProgress`, `failed`, `success`, `deleting`).
    - `message` (string, optional): Error message if synchronization failed.
    - `syncTrigger` (string): The trigger that initiated the synchronization (`on_create`, `manuel`, `scheduled`).
    - `syncType` (string) : Whether to sync only updated events or everything (`regular`, `full`).
    - `updatedAt` (timestamp): Timestamp of the last status update.
  - `targetCalendar` (map)
    - `id` (string): ID of the target calendar.
    - `title` (string): Title of the target calendar, provided by the calendar provider.
    - `description` (string): Description of the target calendar, provided by the calendar provider.
    - `providerAccountId` (string): Unique identifier for the account owning the target calendar (e.g., Google account ID).
    - `providerAccountEmail` (string): Email of the account owning the target calendar.
  - `ruleset` (string, optional): JSON string of a `Ruleset` to apply.
  - `ruleset_error` (string, optional): Error message if generating the ruleset failed.
  - `created_at` (timestamp): Timestamp when the sync profile was created.
  - `lastSuccessfulSync` (timestamp, optional): Timestamp of the last successful synchronization.

- #### `syncStats`
  A collection to track the number of synchronizations performed by a user on a given date. IDs are formatted as `YYYY-MM-DD`.

  **Fields**

  - `syncCount` (integer): Number of synchronizations performed on that date.

### `backendAuthorizations` collection

IDs: concatenation of  `userId` + `providerAccountId`.

**Fields**

- `userId` (string): ID of the user who authorized the backend.
- `provider` (string): Provider of the authorized account (e.g., `google`).
- `providerAccountId` (string): Unique identifier of the authorized provider account.
- `providerAccountEmail` (string): Email of the authorized provider account.
- `accessToken` (string): Access token obtained from the OAuth2 flow.
- `refreshToken` (string): Refresh token obtained from the OAuth2 flow.
- `expirationDate` (timestamp): Expiration date of the credentials.