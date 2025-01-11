from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Message:
    text: str
    color: Optional[str] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    obfuscated: Optional[bool] = None
    click_event: Optional[str] = None
    hover_event: Optional[str] = None
    extra: Optional[List['Message']] = None

    def __init__(self, **kwargs):
        if isinstance(kwargs.get("text"), str):
            self.text = kwargs["text"]
            for field in self.__dataclass_fields__:
                if field != "text" and field in kwargs:
                    setattr(self, field, kwargs[field])
        else:
            # Handle list of Message objects
            self.text = ""
            self.extra = kwargs["text"]

    @property
    def json(self):
        json_blob = {key: value for key, value in {
            "text": self.text,
            "color": self.color,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "strikethrough": self.strikethrough,
            "obfuscated": self.obfuscated,
            "clickEvent": self.click_event,
            "hoverEvent": self.hover_event,
            "extra": [msg.json for msg in self.extra] if self.extra else None
        }.items() if value is not None}

        return json_blob

    @property
    def legacy(self):
        legacy_string = self.text
        if self.color:
            legacy_string = f"§{self.color}{legacy_string}"
        if self.bold:
            legacy_string = f"§l{legacy_string}"
        if self.italic:
            legacy_string = f"§o{legacy_string}"
        if self.underline:
            legacy_string = f"§n{legacy_string}"
        if self.strikethrough:
            legacy_string = f"§m{legacy_string}"
        if self.obfuscated:
            legacy_string = f"§k{legacy_string}"

        if self.extra:
            for extra_message in self.extra:
                legacy_string += extra_message.legacy

        return legacy_string
    

# if __name__ == "__main__":
#     message = Message(text="Hello, world!", color="red", bold=True, italic=True, underline=True, strikethrough=True, obfuscated=True, click_event="run_command", hover_event="show_text", extra=[Message(text="Extra message")])
#     print(message.json)
#     print(message.legacy)