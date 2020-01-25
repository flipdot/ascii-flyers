# ascii-flyer

Generates small flyers for inviting people to events at the hackerspace.

## Installation

Install prerequisites using pip

```
pip install -r requirements.txt
```

## Usage

The following could be used to generate a preview with crop marks:

```
./ascii-flyer.py --title "Brennende Computer" \
                 --description "Daten fangen Feuer? Löschen Sie sie sofort\!" \
                 --datetime "$(date --date='next tuesday 19:23' --iso=m)" \
                 --type "Predigt"\
                 --preview
```

`--preview` can later be dropped to create b/w files.
