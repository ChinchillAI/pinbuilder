{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (
        system:
        let
          inherit (poetry2nix.lib.mkPoetry2Nix { pkgs = pkgs.${system}; }) mkPoetryApplication;
        in
        {
          default = mkPoetryApplication {
            projectDir = self;
            propagatedBuildInputs = with pkgs.${system}; [ openscad ];
          };
        }
      );

      devShells = forAllSystems (
        system:
        let
          inherit (poetry2nix.lib.mkPoetry2Nix { pkgs = pkgs.${system}; }) mkPoetryEnv;
        in
        {
          default =
            (mkPoetryEnv {
              projectDir = self;
              editablePackageSources = {
                pinbuilder = ./pinbuilder;
              };
            }).env.overrideAttrs
              (oldAttrs: {
                buildInputs = with pkgs.${system}; [
                  poetry
                  openscad
                  inkscape
                ];
              });
        }
      );
    };
}
