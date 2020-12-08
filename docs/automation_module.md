# Implementing a new Automation Module

All the automation modules needs to use an NLP model, thus the first step is to add a new automation module or to update a existing one. After that you can start implementing the new module by first copying the automation module template [`docs/templates/automation_module_template.py`](docs/templates/automation_module_template.py) into `lib/automation/modules/`, and then update it with the functionality you want.

## Adding/updating a NLP model

The files that needs to be updated are 

```
requirements.txt
config/language_releases.yaml
config/nlp_models.yaml
```

In `requirments.txt` a link to the releases NLP models must be added or updated.

In `config/language_releases.yaml` a language release must be created. The easiest way is to copy latest release and update it with the new models.

`config/nlp_models.yaml` can be updated by running the install command in the CLI and choosing the new language release that you have added.

## Implementing a followup question

Example:
```
def prompt_date(self):
    """
    An example of how to define a method for asking the user a followup question on the input.
    """
    def callback(followup):
        try:
            when = datetime.fromisoformat(followup.answer)
        except Exception:
            when = None
        return self.prepare_processed(self.to, when, self.body, self.sender)

    question = "\nCould not parse date from input.\nPlease enter date in YYYYMMDD HH:MM format"
    followup = StringFollowup(question, callback)
    return followup
```

Example how to call the followup question from the method `prepare_processed`

```
# If a time is not found then ask a followup question for it.
if not isinstance(when, datetime):
    return self.prompt_date()
```

## Required functions

### \_\_init\_\_

The \_\_init\_\_ method needs to take in the model pool which contains all of NLP models, this enables the module to be able to use the NLP models that are shared between all modules. It also needs to call the Module class that your new module inheritance from. Lastly it is also vital to set the attribute `nlp_model` to `None`.

Here is an example:

```
    def __init__(self, model_pool):
        super(Reminder, self).__init__(model_pool)
        self.nlp_model = None
```

### prepare

This methods job is do all the preparations needed to run the `execute` method, but this method should only be called once for each execution of the module. Thus all the preparations that has to be done again when a followup question has been answered should be in the `prepare_processed` method. 

### prepare\_processed

A requirement of this method is that the NLP model has parsed the input into the following 4 parameter `to, when, body, sender` before calling this method.
* `to` is the list of contacts that user want to send a email to for example.
* `when` is the time, in the schedule it is a dict with the start and end time of an event.
* `body` can be anything.
* `sender` is information of the user, like email information in the email example.

The job of this method is to take the parsed input form the NLP model and process it so that the `execute` method can run. This can be thinks like finding en email related to a name or giving followup questions to the user about missing information.

### execute

The job of `execute` is run the task that this module is for, like sending an email or scheduling a meeting for example. `execute` has no parameters, thus all the information needed has to be set as attributes in the object when running the `prepare_processed` method.

The only thing that this method requires is that it return a string telling the user what the module has done. 

Example:
```
Sent email to johndoe@email.com about "Development"
```

### nlp

This methods job is to run the NLP model on the input and format the output into a usable format using the labels, entity's and tokens that the NLP model gives.

