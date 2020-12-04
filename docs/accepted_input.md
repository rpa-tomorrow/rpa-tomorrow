# Acceptable user input

Since the program is intended to be able to parse and understand clear text as input, to perform various tasks, there is no specific
syntax for the input. However, the program is only able to perform three specific use cases at the moment, these are:

- Sending emails
- Creating reminders
- Scheduling meetings

Because of this the input has to contain a verb connected to one of these use cases in order for the program to understand and invoke a module for execution. Below are the verbs connected to each module, which can be used in the input.

- Send email [send, mail, e-mail, email]
- Reminder [remind, reminder, notify]
- Schedule meeting [book, schedule, meeting]

As long as a module can be invoked after parsing the input you will be prompted about any missing information in the input such as when to schedule the reminder, what should be sent in the email etc.

## Example input

```
remind me to eat in 30 seconds
```

```
send an email to Niklas
```

```
schedule a meeting with John at 13:00
```
