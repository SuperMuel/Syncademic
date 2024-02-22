# Configure Google APIs project

When creating a new synchronization profile, the user must select the target calendar. Thus, we need to show them the list of their calendars. When working with Google Agenda, this is done by using the GoogleCalendar API.

You need to create a Google Cloud for this project, and enable the GoogleCalendar API : https://cloud.google.com/apis/docs/getting-started

Once the GoogleCalendar API has been enabled, you'll need to setup [billing](https://cloud.google.com/apis/docs/getting-started#enabling_billing).

Also follow the instructions give on [google_sign_in](https://pub.dev/packages/google_sign_in) and [google_sign_in_web](https://pub.dev/packages/google_sign_in_web)

To see how we use the API in the Flutter APP, check this guide https://docs.flutter.dev/data-and-backend/google-apis

Once everything is setup, you'll need to specify your OAuth clientID in `.env`. For this, you can duplicate the `.env.template` file to `.env` and edit it accordingly.
