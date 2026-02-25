import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


LINK_PATTERN = re.compile(r"(?:https?://)?discord\.gg/([A-Za-z0-9]+)", re.IGNORECASE)


def extract_links(text: str) -> list[str]:
    links = []
    for match in LINK_PATTERN.finditer(text):
        code = match.group(1)
        links.append(f"discord.gg/{code}")
    return links


def load_file_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def unique_ordered(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


class LinkApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Discord Invite Link Identifier")
        self.root.geometry("860x520")
        self.root.minsize(780, 480)

        self.old_path = tk.StringVar()
        self.new_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready.")

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(container)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        left_frame = ttk.LabelFrame(input_frame, text="Old links (.txt)")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        right_frame = ttk.LabelFrame(input_frame, text="New links (.txt)")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        self._build_file_picker(left_frame, self.old_path, self._browse_old)
        self._build_file_picker(right_frame, self.new_path, self._browse_new)

        action_frame = ttk.Frame(container)
        action_frame.pack(fill=tk.X)

        process_button = ttk.Button(action_frame, text="Process", command=self._process)
        process_button.pack(side=tk.LEFT)

        save_button = ttk.Button(action_frame, text="Save Results", command=self._save_results)
        save_button.pack(side=tk.LEFT, padx=(8, 0))

        result_frame = ttk.LabelFrame(container, text="New Discord links")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.result_text = tk.Text(result_frame, wrap=tk.NONE, height=12)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        status_bar = ttk.Label(container, textvariable=self.status_text, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(8, 0))

    def _build_file_picker(self, parent: ttk.LabelFrame, path_var: tk.StringVar, command) -> None:
        entry = ttk.Entry(parent, textvariable=path_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)

        button = ttk.Button(parent, text="Browse", command=command)
        button.pack(side=tk.LEFT, padx=(0, 8), pady=8)

    def _browse_old(self) -> None:
        self._select_file(self.old_path, "Select old links file")

    def _browse_new(self) -> None:
        self._select_file(self.new_path, "Select new links file")

    def _select_file(self, target: tk.StringVar, title: str) -> None:
        path = filedialog.askopenfilename(
            title=title,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            target.set(path)

    def _process(self) -> None:
        old_path = self.old_path.get().strip()
        new_path = self.new_path.get().strip()

        if not old_path or not new_path:
            messagebox.showwarning("Missing file", "Please select both text files first.")
            return

        try:
            old_text = load_file_text(old_path)
            new_text = load_file_text(new_path)
        except OSError as exc:
            messagebox.showerror("File error", f"Could not read file: {exc}")
            return

        old_links = unique_ordered(extract_links(old_text))
        new_links = unique_ordered(extract_links(new_text))

        old_set = set(old_links)
        only_new = [link for link in new_links if link not in old_set]

        self.result_text.delete("1.0", tk.END)
        if only_new:
            self.result_text.insert(tk.END, "\n".join(only_new))
        else:
            self.result_text.insert(tk.END, "No new links found.")

        self.status_text.set(
            f"Old links: {len(old_links)} | New links: {len(new_links)} | Extracted: {len(only_new)}"
        )

    def _save_results(self) -> None:
        content = self.result_text.get("1.0", tk.END).strip()
        if not content or content == "No new links found.":
            messagebox.showinfo("Nothing to save", "There are no new links to save.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save new links",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as handle:
                handle.write(content)
        except OSError as exc:
            messagebox.showerror("Save error", f"Could not save file: {exc}")
            return

        self.status_text.set(f"Saved to {save_path}")


def main() -> None:
    root = tk.Tk()
    LinkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
