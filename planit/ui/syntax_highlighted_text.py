
import tkinter as tk
import re


class SyntaxHighlightedText (tk.Text):
    def __init__(self, root, **kwargs):
        super(SyntaxHighlightedText, self).__init__(root, **kwargs)
        # self.bind("<KeyRelease>", lambda e: self._highlight_text())
        self.bind("<<Modified>>", self._on_true_change)

        self.patterns = []
        self.state = "None"

    def _on_true_change(self, event):
        # Prevent this event from being called twice
        if self.edit_modified():
            self._highlight_text()

        self.edit_modified(False)

    def _clear_highlighting(self):
        # Clear the existing tags
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", tk.END)

    def _highlight_text(self):
        self._clear_highlighting()

        text = self.get_text()
        for pattern, tag in self.patterns:
            cursor_pos = (1, 0)

            def consume(t: str):
                nonlocal cursor_pos

                line, col = cursor_pos

                if "\n" in t:
                    col = len(t) - t.rfind("\n") - 1
                    line += t.count("\n")
                else:
                    col += len(t)

                cursor_pos = (line, col)

            def cursor_to_str():
                line, col = cursor_pos
                return "{}.{}".format(line, col)

            last_idx = 0
            for match in re.finditer(pattern, text):
                start_idx = match.start()

                text_leading_up_to_match = text[last_idx:start_idx]
                consume(text_leading_up_to_match)
                start_pos = cursor_to_str()

                matched_text = match.group(0)
                consume(matched_text)
                end_pos = cursor_to_str()
                last_idx = start_idx + len(matched_text)

                self.tag_add(tag, start_pos, end_pos)

    def _highlight_text_via_tk(self):
        # Clear the existing tags
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", tk.END)

        for pattern, tag in self.patterns:
            self.mark_set("matchEnd", "1.0")

            count = tk.IntVar()
            while True:
                start_index = self.search(pattern, "matchEnd", tk.END, count=count)

                if start_index == "": break
                # Pattern matches 0 characters
                if count.get() == 0: break

                self.mark_set("matchEnd", f"{start_index}+{count.get()}c")
                self.tag_add(tag, start_index, "matchEnd")

    def highlight(self, pattern, **style):
        name = id(pattern)
        self.tag_config(name, **style)
        self.patterns.append((pattern, name))

    def get_text(self):
        return self.get("1.0", tk.END)
