# assbot
[![actions-workflow-test][actions-workflow-test-badge]][actions-workflow-test]

Handy companion for [@assthread](https://t.me/assthread) -- pseudo-anonymous chatting place with free speech and no censorship.

## Available commands
- `/start` - start the bot
- `/test` - check if the bot is alive
- `/whoami` - returns your Telegram ID and username
- `/uname` - returns `uname -a` output
- `/hash` - checks if running `main.py` is equal to what is in the `master` branch
- `/loglevel` - [admin only] change log level during runtime
- `/ping` - [admin only] check if bot is able to reach specified user ID (or everyone from subscribers list if no ID is specified)
- `/send_poll` - [admin only] start activity check poll for all subscruibers
- `/stop_poll` - [admin only] stop activity check poll (on reply to poll message)

## Quick start
**BE AWARE TO RUN IT WITH YOUR FAKE ACCOUNT**
Telegram could simply log you off and you will never see your account again.
0. Create new bot via [@BotFather](t.me/BotFather) and get bot token.
1. Add bot to your channel and grant it admin privileges.
2. Obtain `API_ID` and `API_HASH` from [my.telegram.org](my.telegram.org) (this is required for some user interactions).
### Docker way
Regenerate `cfg.py` file:
```
docker run -it \
  -e API_ID=<...> \
  -e API_HASH=<...> \
  -e LOGLEVEL=INFO \
  -e CHANNEL=<...> \
  -e BOT_NAME=<...> \
  -v $(pwd):/workspace \
  -u $(id -u):$(id -g) \
  ghcr.io/tsunamaru/assbot/base:latest \
  python helpers.py
```
Build it:
```
docker build . \
  -f build/ci-build.Dockerfile \
  -t ghcr.io/tsunamaru/assbot/ci-build:latest
```
Run it:
```
docker run -it \
  -e TOKEN=<...> \
  -e CHANNEL=<...> \
  -e LOGLEVEL=INFO \
  -e ADMIN=<...> \
  ghcr.io/tsunamaru/assbot/ci-build:latest
```
### Usual way
Virtualenv usage is optional, but highly recommended:
```
virtualenv venv
source venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Make your own `.env` file and fill it with your data:
```
cp .env.example .env
vim .env
```
Regenerate `cfg.py` file:
```
python3 helpers.py
```
Run it:
```
python3 main.py
```

## Kubernetes deployment
See example in ./k8s directory.

## License
[The Unlicense](LICENSE)

<!-- badge links -->

[actions-workflow-test]: https://github.com/tsunamaru/assbot/actions?query=workflow%3ABuild%20and%20Deploy
[actions-workflow-test-badge]: https://img.shields.io/github/actions/workflow/status/tsunamaru/assbot/001-main.yaml?branch=master&label=CI&logo=github&style=for-the-badge
