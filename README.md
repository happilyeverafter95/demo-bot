# demo-bot

Simple chatbot written in Python 3.7.

## Local Dev Setup

1. Install requirements.txt by running `pip install -r requirements.txt`
2. Install Spacy models: 
```
python3 -m spacy download en_core_web_md
python3 -m spacy link en_core_web_md en
```

To start the bot, run:
```
rasa run -m models --enable-api --cors "*" --debug & rasa run actions
```

This starts the server at http://localhost:5005

If you are deploying the bot to another platform (such as Facebook messenger), add `--credentials credentials.yml` after `--debug` and fill in the necessary credentials.

