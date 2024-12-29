# Overview #
[![Join the chat at https://gitter.im/benbaptist/wrapper.py](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/benbaptist/wrapper.py?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Wrapper.py is an easy to use Minecraft server wrapper, for adding extra functionality on a vanilla Minecraft server without modifying
the server jar. It comes with a relatively simple and straight-forward - yet powerful - plugin API that can be used
to create Bukkit-like plugins without any server modding. No Java knowledge required.

In addition to plugins, it also comes with a dashboard, a backup system, and a RESTful API.

Join us on Gitter!

# Quick Start #
### Stable branch
```
# Install stable Wrapper.py
pip3 install https://github.com/benbaptist/wrapper.py/archive/master.zip
```

### Development branch
```
# Install development (unstable) Wrapper.py
pip3 install https://github.com/benbaptist/wrapper.py/archive/development.zip
```

Just run `mcwrapper` in the working directory of your Minecraft server to start.
On first start, it'll present you with a setup wizard. After you complete, re-run `mcwrapper` again,
and enjoy.

You may need to adjust your shell's $PATH to incorporate your local bin folder, depending on your system or how you installed Wrapper. For some systems, adding this to your .bashrc may work:

```
export PATH=$PATH:~/.local/bin
```

Wrapper.py will automatically accept the Minecraft server EULA on your behalf, if you have not already done so.

# Plugins #
[Here's a repository filled with plugins](https://github.com/benbaptist/wrapper-plugins) to get you started.

# Wrapper.py 2.0 #
This is a complete re-write of Wrapper.py, and is focused on being extremely lightweight and clean. For the original 1.x repository, [click here](http://github.com/benbaptist/minecraft-wrapper).
