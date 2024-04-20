# syncademic_app

## Getting Started

### Firebase

Firebase is used for this project.

Go to [this guide](https://firebase.google.com/docs/flutter/setup) to :

- Install the firebase CLI
- Install the fluterfire CLI
- Run `flutterfire configure`

### Release signing

Add the release keystore file at [./android/app/release.keystore](./android/app/release.keystore)

Create a file named [project]/android/key.properties that contains a reference to your keystore.

```properties
storePassword=<password>
keyPassword=<password>
keyAlias=syncademic_release_sha1_key
storeFile=release.keystore
```

For more information check https://docs.flutter.dev/deployment/android
