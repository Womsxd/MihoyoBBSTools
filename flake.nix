{
  description = "Flake utils demo";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      rec {
        # Python 及依赖包
        packages.python3 = pkgs.python3.withPackages (
          python-pkgs: with python-pkgs; [
            httpx
            pyyaml
            pytz
          ]
        );

        # 打包 Python 文件作为库
        packages.lib = pkgs.stdenvNoCC.mkDerivation {
          pname = "mihoyo-bbs-tools";
          version = "0.1.0";
          src = ./.;
          installPhase = ''
            mkdir -p $out/
            cp *.py $out/
          '';
        };

        # 包装为 Bash 脚本
        packages.script =
          let
            python3 = "${packages.python3}/bin/python3";
          in
          pkgs.writeShellScriptBin "mihoyo-bbs-tools" ''
            # 根据环境变量决定执行 main 还是 main_multi
            if [[ "$AutoMihoyoBBS_config_multi" = "1" ]]; then
              ${python3} ${packages.lib}/main_multi.py autorun "$@"
            else
              ${python3} ${packages.lib}/main.py "$@"
            fi
          '';

        # 默认為 Bash 脚本
        packages.default = packages.script;
      }
    )
    // flake-utils.lib.eachDefaultSystemPassThrough (system: {
      # Home Manager 模块
      homeModules.default =
        {
          config,
          pkgs,
          lib,
          ...
        }:
        let
          cfg = config.services.mihoyo-bbs-tools;
          format = pkgs.formats.yaml { };
        in
        {
          # 选项定义
          options = {
            services.mihoyo-bbs-tools = {
              # 启用
              enable = lib.mkEnableOption "mihoyo-bbs-tools";

              # 使用哪个包
              package = lib.mkOption {
                type = lib.types.package;
                default = self.outputs.packages.${system}.default;
              };

              # 运行时间
              onCalendar = lib.mkOption {
                type = lib.types.str;
                default = "09:30";
                example = "daily";
                description = ''
                  运行时间，默认每天 9:30 运行。

                  具体具体配置请参阅 {manpage}`systemd.time(7)`
                '';
              };

              # 立即执行
              persistent = lib.mkOption {
                type = lib.types.bool;
                default = true;
                example = false;
                description = ''
                  服务启动后是否立即执行。
                '';
              };

              # 配置文件
              settings = lib.mkOption {
                type = lib.types.attrsOf format.type;
                default = { };
                example = {
                  config = {
                    enable = true;
                    version = 13;
                    push = "";
                    account = {
                      cookie = "<你的 Cookie>";
                    };
                  };
                };
                description = ''
                  配置文件列表，单用户使用 `config`。

                  请参考 `config/config.yaml.example`。
                '';
              };

              # 额外环境设置
              extraEnvironments = lib.mkOption {
                type = lib.types.attrsOf lib.types.str;
                default = { };
                example = {
                  AutoMihoyoBBS_config_multi = 1;
                };
                description = ''
                  除了 `AutoMihoyoBBS_config_path` 之外需要配置的环境变量。
                '';
              };
            };
          };

          # 选项实现
          config = lib.mkIf cfg.enable {
            # 保存配置文件到 ~/.config/mihoyo-bbs-tools
            xdg.configFile = lib.attrsets.concatMapAttrs (name: value: {
              "mihoyo-bbs-tools/${name}.yaml".source = format.generate "${name}.yaml" value;
            }) cfg.settings;

            # Service 定义
            systemd.user.services.mihoyo-bbs-tools = {
              Unit = {
                Description = "Womsxd/AutoMihoyoBBS，米游社相关脚本";
              };
              Install = {
                WantedBy = [ "default.target" ];
              };
              Service = {
                ExecStart = "${cfg.package}/bin/mihoyo-bbs-tools";
                Environment = [
                  # 默认设置 config_path 变量
                  "AutoMihoyoBBS_config_path=${config.xdg.configHome}/mihoyo-bbs-tools"
                ] ++ lib.attrsets.mapAttrsToList (name: value: "${name}=${value}") cfg.extraEnvironments;
              };
            };

            # Timer 定义
            systemd.user.timers.mihoyo-bbs-tools = {
              Unit = {
                Description = "每日运行米游社签到";
              };
              Timer = {
                OnCalendar = cfg.onCalendar;
                Persistent = cfg.persistent;
                # 参考 `start.bash` 设置
                RandomizedDelaySec = "20min";
              };
              Install = {
                WantedBy = [ "timers.target" ];
              };
            };
          };
        };
    });
}
