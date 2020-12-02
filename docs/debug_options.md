# Development information and debug options
## Debug SMTP server

It can be nice to test the Send automation module (sends emails) using a local SMTP debugging server. This can be done by running

```
python -m smtpd -n -c DebuggingServer localhost:1025
```

in your terminal. A local SMTP debugging server is now running on `localhost:1025` and the predefined user `John Doe` in [config/user.yaml](config/user.yaml) can be used to send emails to this local server. If an email is sent using the module you should now be able to see it in the terminal.
