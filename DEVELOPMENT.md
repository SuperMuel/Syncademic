# Local Development

### Firebase CLI
1. Install the Firebase CLI
2. Login to Firebase
3. Select or create the project


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


