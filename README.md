# 🧙🏼‍♂️ Wizz Bot

A simple Discord Bot which will download and display artwork for any given wizard from [Forgotten Runes Wizard Cult](https://forgottenrunes.com).

## Commands

The available bot commands are:
- `!pic` - Shows the original wizard artwork
- `!gif` - Shows an animated GIF of the wizard turnaround
- `!gifbig` - Shows an large animated GIF of the wizard turnaround
- `!mug` - Shows a mughsot with a random background and frame
- `!gifmug` - Shows an animated mughsot with a random background and frame
- `!gifmugbig` - Shows a large animated mughsot with a random background and frame

### 🤖 Bot

To run your own version of the Bot, set one up in the Discord Developer Portal, and put your own token in `creds.json`.

### 🖥 CLI

You can also use this as a standalone tool for downloading artwork; Either supply a list of wizard IDs as arguments, or run without arguments to enter interactive mode.

For example `$ python3 wizz.py 8679` will download and extract the artwork for wizard numer 8679, aka. Sorcerer Ilyas of the Fey, to the current working directory.

### Examples
`!gif 8679`

![8679s](https://user-images.githubusercontent.com/91800037/137698245-975da5e5-293e-4f8f-ad66-49fa426ff59a.gif)

`!gifbig 549`

![549](https://user-images.githubusercontent.com/91800037/137698378-84dc365f-f956-4d92-b92a-44e8c896642a.gif)

`!mug 0`

![0-mugshot-pfp](https://user-images.githubusercontent.com/91800037/137698474-571e1d76-486d-4f79-a2d1-bf08484fca0b.png)

`!gifmugbig 1`

![1-mugshot](https://user-images.githubusercontent.com/91800037/137698648-4b877e2d-b532-4994-9bab-4d9de29edf9f.gif)
