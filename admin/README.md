## Setting up Google Cloud Credentials for Local Development

To run the admin panel locally, you need to provide Google Cloud credentials so that the application can access Firebase services (Firestore, Storage, and Authentication). We use a service account for this.

**Steps:**

1.  **Create a Service Account:**
    *   Go to the [IAM & Admin > Service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) page in the Google Cloud Console for your Firebase project.
    *   Click "+ CREATE SERVICE ACCOUNT".
    *   Give it a descriptive name (e.g., `syncademic-admin-local`).
    *   **Grant Roles:** Grant the service account the following roles:
        *   **Storage Object Viewer (`roles/storage.objectViewer`):** Allows listing and reading files in your Storage bucket.
        *   **Firebase Admin SDK Administrator Service Agent (`roles/firebase.admin`):** Provides broad access to Firebase services (use more granular roles in production).
        *   **Service Account Token Creator (`roles/iam.serviceAccountTokenCreator`):** Allows the app to impersonate the service account.
    *   Click "DONE".

2.  **Download the Service Account Key:**
    *   On the Service accounts page, find your newly created service account.
    *   Click the three dots (...) in the "Actions" column and select "Manage keys".
    *   Click "ADD KEY" -> "Create new key".
    *   Choose "JSON" as the key type.
    *   Click "CREATE". A JSON file containing the service account credentials will be downloaded.  **Keep this file secure!**  Do *not* commit it to your Git repository.

3.  **Set the `GOOGLE_APPLICATION_CREDENTIALS` Environment Variable:**
    *   Create a `.env` file in the `admin/` directory (if it doesn't exist).
    *   Add the following line to your `.env` file, replacing `/path/to/your/keyfile.json` with the *absolute* path to the downloaded JSON key file:

        ```
        GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json
        ```

    *   **Important:** Ensure that the `.env` file is included in your `.gitignore` file to prevent accidental commits of your credentials.

4.  **Restart Streamlit:** After setting the environment variable, restart your Streamlit app for the changes to take effect.

**Security Note:** The `roles/firebase.admin` role grants broad access. For production environments, create a custom role with the *minimum* necessary permissions.  The service account key file should be treated as a sensitive secret.