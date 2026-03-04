import json
import sys
import os

from .migration import migration
from .dash_flow import dash_flow

stages = (
    migration,
    dash_flow,
)

class Wizard:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.log = wrapper.log
        self.config = wrapper.config
        self.mojang = wrapper.mojang

    def ask_bool(self, msg):
        while True:
            answer = input("%s (y/n): " % msg).lower()

            if answer == "y":
                return True
            elif answer == "n":
                return False
            else:
                print("Please type 'y' or 'n', and then hit enter.")

    def ask_int(self, msg, safe_range=None):
        if safe_range:
            safe_min = safe_range[0]
            safe_max = safe_range[1]

        while True:
            if safe_range:
                answer = input("%s (%s-%s): " % (msg, safe_min, safe_max))
            else:
                answer = input("%s (number): " % msg)

            try:
                answer = int(answer)

                if safe_range:
                    if answer < safe_min or answer > safe_max:
                        print("Please enter a number between %s and %s,"
                            "and then hit enter."
                            % (safe_min, safe_max))
                        continue

                return answer
            except:
                print("Please enter a number, and then hit enter.")

    def ask_str(self, msg, default=None, min_len=None):
        while True:
            if default:
                answer = input("%s (default: %s): " % (msg, default))
            else:
                answer = input("%s: " % msg)

            if min_len != None:
                if len(answer) < min_len:
                    print("Your answer must be at least %s characters." % min_len)

            if len(answer) < 1:
                if default:
                    return default
                else:
                    print("Please enter your answer, and then hit enter.")
                    continue

            return answer
        
    def run_wrap(self):
        try:
            self.run()
        except KeyboardInterrupt:
            # Cleanup and exit gracefully
            try:
                os.remove("wrapper-data/config.json")
            except FileNotFoundError:
                pass
            
            print("\nWizard cancelled. No changes have been made.")
            sys.exit(0)

    def run(self):
        print("* Welcome to Wrapper.py!")
        print("* Before we begin, let's get a few things set up.")
        print("* By continuing, you are agreeing to Mojang's EULA.")
        print("-" * 16)

        for stage in stages:
            stage(self)

        # If we made it here, something went wrong. This should never happen, since the appropriate stages should call sys.exit() when exited.
        print("Something went wrong during the setup process. Please try again.")
        sys.exit(-1)
