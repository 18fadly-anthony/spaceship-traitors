# Spaceship Traitors

an Among Us spin off game played via a telegram bot

## Installation

Install Python and the python-telegram-bot package

on NixOS use:

```
with pkgs;
let
  my-python-packages = python-packages: with python-packages; [
    python-telegram-bot
  ];
  python-with-my-packages = python3.withPackages my-python-packages;
in
...

environment.systemPackages = with pkgs; [
  ...
  python-with-my-packages
  ...
];
```

```
git clone --depth 1 https://github.com/18fadly-anthony/spaceship-traitors
```

## Running

```
$ cd spaceship-traitors
$ ./bot.py 'API_KEY_HERE'
```
