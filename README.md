# Snips-Glückskekse 🥠
A app for Snips.ai for speaking fortune cookies from package "fortunes-de".



## Installation
**Important:** The following instructions assume that [Snips](https://snips.gitbook.io/documentation/snips-basics) is
already configured and running on your device. [SAM](https://snips.gitbook.io/getting-started/installation) should
also already be set up and connected to your device and your account.

1. Install package `fortunes-de` on your Raspberry Pi or Linux OS, where Snips (not SAM!) runs on with:

      ```bash
      sudo apt update && sudo apt install -y fortunes-de
      ```
    This step must be completed *before* installing the assistant.
    
2. In the German [app store](https://console.snips.ai/) add the
app `Witze & Glückskekse` (by domi; [this](https://console.snips.ai/app-editor/bundle_7ZYEq522Ang)) to
your *German* assistant.

3. If you already have the same assistant on your platform, update it
(with [Sam](https://snips.gitbook.io/getting-started/installation)) with:
      ```bash
      sam update-assistant
      ```
      
   Otherwise install the assistant on the platform with [Sam](https://snips.gitbook.io/getting-started/installation)
   with the following command to choose it (if you have multiple assistants in your Snips console):
      ```bash
      sam install assistant
      ```

    That's it!
    
## Configuration

In your Snips console you can change some values by clicking on this skill (`Witze & Glückskekse`).

The following should explain these parameters:
- With the parameter `fortunes_max_laenge` you can set the maximum length of all the fortunes,
so that no very long fortune cookies are read out. The default is 100 characters.
- The value in `max_frage_wdh` controls the number of repetitions of the question
    "Noch ein Spruch?" if the answer was not understood. The default is one repetition.
    
If you have changed the values, you must then run
  ```bash
  sam update-assistant
  ```
so that the config is on your device.

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

## Todo

- Publish cookies over MQTT

## Contribution

Please report errors (you can see them with `sam service log`) and bugs by
opening a [new issue](https://github.com/MrJohnZoidberg/Snips-Glueckskekse/issues/new).
You can also write other ideas for this skill. Thank you for your contribution.
