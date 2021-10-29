# Planit

Desktop application for planning the cultivation of vegetable plants.

---

**Tip**: How to run a python file directly without breaking relative imports:

To run `planit/genetic/genetic_algorithm.py` run the following command in your terminal:
`python -m planit.genetic.genetic_algorithm`

**Tip**: Building an executable

Make sure you are in the planit root folder:

```batch
pip install auto-py-to-exe
```

```batch
auto-py-to-exe -c build_settings.json
```

After opening auto-py-to-exe, you'll have to change the path to the `main.py` file and, under the <kbd>Additional Files</kbd> tab, change the path to the `resources` folder.

Then just press <kbd>CONVERT .PY to .EXE</kbd>. The output files are in `output/`
