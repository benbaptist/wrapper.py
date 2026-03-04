def dash_flow(self):
    use_dash = self.ask_bool("Would you like to use the browser-based dashboard?")

    if use_dash:
        port = self.ask_int("What port would you like the dashboard to be on?",
            safe_range=(1, 65535))
        bind = self.ask_str("What IP would you like the dashboard to bind to?"
            , default="0.0.0.0")

        password = self.ask_str("Please enter a strong password to use", min_len=8)

        self.config["dashboard"]["enable"] = True
        self.config["dashboard"]["bind"]["ip"] = bind
        self.config["dashboard"]["bind"]["port"] = port
        self.config["dashboard"]["root-password"] = password

        print("You're all set to use the dashboard.")
        print("You'll access it using this URL: http://%s:%s" % (bind, port))
        print("When prompted, the username is 'root', and the password "
        "is the one you provided.")

        print("-" * 16)
        print("Wrapper.py will now save changes and exit. You may "
        "continue setting up Wrapper through the dashboard.")

        self.config.save()

        sys.exit(0)
    else:
        # Find server jars
        server_jars = []
        for fn in os.listdir("."):
            try:
                name, ext = fn.rsplit(".", 1)
            except:
                name, ext = fn, None

            if ext == "jar":
                server_jars.append(fn)

        download_jar = False

        if len(server_jars) > 0:
            print("Please pick a server jar to use from the list:")

            for i, jar in enumerate(server_jars):
                print(" - #%s: %s" % (i, jar))

            print(" - #%s: Download a new jar..." % len(server_jars))

            jar_to_use = self.ask_int("Pick an option", safe_range=(0, len(server_jars)))

            if jar_to_use == len(server_jars):
                download_jar = True
            else:
                self.config["server"]["jar"] = server_jars[jar_to_use]

        else:
            if self.ask_bool("Wrapper.py could not detect any existing server"
                "jars in this folder. Would you like to download one?"):
                download_jar = True

        if download_jar:
            all_server_jars = self.mojang.servers.versions

            latest_snapshot = None
            latest_release = None

            for server_jar in all_server_jars:
                print(server_jar["type"], server_jar["id"])
                if server_jar["type"] == "snapshot":
                    latest_snapshot = server_jar
                    break

            for server_jar in all_server_jars:
                if server_jar["type"] == "release":
                    latest_release = server_jar
                    break

            print("-" * 16)
            print("Pick a server jar to use:")

            print(" - #1: Latest release (%s)" % latest_release["id"])
            print(" - #2: Latest snapshot (%s)" % latest_snapshot["id"])
            print(" - #3: Cancel")

            option = self.ask_int("Select a download", safe_range=(1, 3))
            if option == 1:
                print("Downloading the latest release...")
                server_jar_path = self.mojang.servers.get_jar(
                    latest_release["id"]
                )

                self.config["server"]["jar"] = server_jar_path
            elif option == 2:
                print("Downloading the latest snapshot...")
                server_jar_path = self.mojang.servers.get_jar(
                    latest_snapshot["id"]
                )

                self.config["server"]["jar"] = server_jar_path

        print("You're all set. Wrapper.py will save and exit. Re-run Wrapper.py"
            "to get started with all your Wrappery wrappness.")

        self.config.save()

        sys.exit(0)