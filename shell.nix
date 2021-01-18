with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "spaceship-traitors-env";
  buildInputs = [
    # System requirements.
    readline

    # Python requirements (enough to get a virtualenv going).
    python3Full
    python3Packages.python-telegram-bot
  ];
  src = null;
  shellHook = ''
    # Allow the use of wheels.
    SOURCE_DATE_EPOCH=$(date +%s)

    # Augment the dynamic linker path
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${R}/lib/R/lib:${readline}/lib
  '';
}
