{
  description = "A nix flake for working with vanilla rust";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    naersk.url = "github:nix-community/naersk";

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      naersk,
      flake-utils,
      ...
    }:

    flake-utils.lib.eachDefaultSystem (
      system:
      let

        pkgs = nixpkgs.legacyPackages.${system};
        naerskLib = pkgs.callPackages naersk { };

        base_lib = with pkgs; [
        ];

        std_bin = with pkgs; [
          svelte-language-server
          nodejs
          typescript-language-server
          tailwindcss
          tailwindcss-language-server
        ];

        link_flag = base_lib ++ std_bin;
      in
      {

        devShell = pkgs.mkShell {
          packages = std_bin;
        };

      }
    );
}
