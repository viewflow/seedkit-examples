# README demo GIF

Re-records `.github/demo.gif` — the terminal demo embedded in the seedkit README.

Needs [vhs](https://github.com/charmbracelet/vhs) + `tree` (`brew install vhs tree`).
The tree shown is the real `07-vps-sqlite-saas` output in this repo. The GIF
itself belongs to the seedkit README, so the last step writes across to the
sibling `seedkit/` checkout.

```sh
cd train/demo
vhs demo.tape
cp seedkit-demo.gif ../../../seedkit/.github/demo.gif
```

`demo.sh` is the staged REPL the tape drives: typed prompt, generation steps,
line-by-line file tree, closing boot line.
