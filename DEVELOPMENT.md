# Local Development

### Firebase CLI
1. Install the [Firebase CLI](https://firebase.google.com/docs/cli)
2. Login to Firebase
```bash
firebase login
```
3. Select or create the project
```bash
# List available projects
firebase projects:list

# Select a project
firebase use <project-id>
```

### FlutterFire
Under `syncademic_app`, install and configure [FlutterFire](https://firebase.google.com/docs/flutter/setup?platform=web).

### Setup the Firebase Emulator Suite
This will allow you to emulate Firestore (the DB), Firebase Auth to authenticate users, and Firebase Functions to run server-side code.

If not setup already, run the following to initialize the Firebase Emulator Suite:
```bash
firebase init emulators
```

To start the emulators, run:
```bash
firebase emulators:start
```




# Deploy

### Deploy cloud functions

```bash
firebase deploy --only functions
```