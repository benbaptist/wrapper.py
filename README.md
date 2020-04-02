# Overview #
[![Join the chat at https://gitter.im/benbaptist/wrapper.py](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/benbaptist/minecraft-wrapper?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Wrapper.py is an easy to use Minecraft server wrapper for adding extra functionality into the server without modifying
the Minecraft server jar. It comes with a relatively simple and straight-forward - yet powerful - plugin API that can be used
to create Bukkit-like plugins without any server modding.

Join us on Gitter!

# Quick Start #
```
# Install dependencies
pip install -r https://raw.githubusercontent.com/benbaptist/wrapper.py/master/requirements.txt

# Install stable Wrapper.py
pip install https://github.com/benbaptist/wrapper.py/archive/master.zip
```

Just run `mcwrapper` in the working directory of your Minecraft server to start.
On first start, it'll write a configuration file to `wrapper-data/config.json`. Edit to your needs, and then run `mcwrapper` again.

You may need to adjust your shell's $PATH to incorporate your local bin folder, depending on your system. For some systems, adding this to your .bashrc may work:

```
export PATH=$PATH:~/.local/bin
```

Wrapper.py will automatically accept the Minecraft server EULA on your behalf.

# Wrapper.py 2.0 #
This is a complete re-write of Wrapper.py, and is focused on being extremely lightweight and clean. For the original 1.x repository, [http://github.com/benbaptist/minecraft-wrapper](click here).
