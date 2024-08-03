{ pkgs ? import <nixpkgs> }:
let
  flask = pkgs.python3Packages.flask;
in
  flask
