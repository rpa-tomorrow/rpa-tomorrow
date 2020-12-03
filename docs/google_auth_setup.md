# Google Auth Setup
## Google QAuth 2.0 client secret

Since the [schedule module](lib/automate/modules/schedule.py), responsible for scheduling meetings, uses the Google Calendar API some setup is required
for this module to work.
Follow this [Google guide](https://support.google.com/cloud/answer/6158849?hl=en) and create a Google Calendar API.

The scope of the credentials needs to set to

```
https://www.googleapis.com/auth/calendar.events.owned
https://www.googleapis.com/auth/calendar.readonly
https://www.googleapis.com/auth/contacts.readonly
https://www.googleapis.com/auth/contacts.other.readonly
https://www.googleapis.com/auth/directory.readonly
```

After that download the credentials and put it in `substorm-nlp/` directory, also name it `client_secret.json`.

Now the schedule module should work and any created meetings should show up in the calendar of the account you created the credentials for.

## Google service account

To use the Speech-to-Text feature of the program a Google service account key is required, since it uses the Google [Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text).

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/apis/) and make sure the correct project is selected.
2. Go to `credentials`
3. Click `Create credentials` and select `Service account`
4. Fill in the required fields, select `Owner` role
5. Click on the newly created service account, under Keys press `Add key` and select `Create new key`
6. When prompted to choose key type select `JSON`
7. Save the key as `service_account.json`
8. Move the key into the project folder
9. [Enable](https://console.cloud.google.com/apis/library/speech.googleapis.com) the Cloud Speech-to-Text API for the same project you created the key for. **Please note that this Google service is only free for the first 60 minutes of Speech-to-Text processed each month. If you can I recommend starting a [trial account](https://console.cloud.google.com/freetrial/signup/tos) which will give you \$300 free credits.**
