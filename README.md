# Snips-Glückskekse
A skill for Snips.ai for speaking fortune cookies from package "fortunes-de".



## Installation

- Install package `fortunes-de` on your Raspberry Pi or Linux OS, where Snips runs on with

  ```bash
  sudo apt update && sudo apt install fortunes-de
  ```

- In the German [skill store](https://console.snips.ai/) add the skill `Witze und Glückskekse` to your *German* assistant

- With the parameter `fortunes_max_laenge` you can set the maximum length of all the fortunes, so that no very long fortune cookies are read out. The default is 100 characters.

- Then install your assistant on the platform with [Sam](https://snips.gitbook.io/getting-started/installation):

  ```bash
  sam install assistant
  ```

- And install the skills included in your assistant:

  ```bash
  sam install skills
  ```

## Usage

You can ask for a joke with your wakeword (usually *Hey Snips*) and then

- *erzähle mir einen Witz*
- *sag mir etwas witziges*
- *kannst du mir einen Witz erzählen*
- [...]

Or you can ask for a fortune from a random category:

- *kann ich ein Fortune Keks hören*
- *gib uns ein Fortune Keks*
- *sage ein Fortune*
- *kannst du bitte Fortunes ausgeben*

But you can also ask for another category of the `fortunes-de` package, for example:

- *sage mir etwas aus der Kategorie Windows/Microsoft*
- *spreche einen Spruch aus der Kategorie Warmduscher*
- *gebe einen Spruch mit Wussten Sie aus*
- *kannst du mir bitte eine Bauernregel sagen*
- *sage etwas aus der Kategorie Quizfrage*
- *lese ein Sprichwort vor*
- [...]

By the way, the categories used of the `fortunes-de` package are as follows:

- `tips`
- `sprueche`
- `wusstensie`
- `murphy`
- `fussball`
- `bahnhof`
- `ms`
- `letzteworte`
- `regeln`
- `quiz`
- `sprichworte`
- `unfug`
- `witze`
- `warmduscher`
- `zitate`
- `kinderzitate`
- `doppelsinnig`
- `lieberals`

## TODO

At this time there are no TODOs.
