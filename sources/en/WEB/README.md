# WEB: World English Bible

Sourced from: https://github.com/TehShrike/world-english-bible/tree/v1.0.1

**License:** Public Domain

## Instructions

Clone the source repository, copy its `json` directory into this folder (replacing the existing `json` directory), then run the conversion script to regenerate `WEB.json`:

```sh
git clone --depth 1 --branch v1.0.1 https://github.com/TehShrike/world-english-bible

rm -rf sources/en/WEB/json
cp -R world-english-bible/json sources/en/WEB/json

python scripts/convert_webtranslation_to_json.py

rm -rf world-english-bible
```
