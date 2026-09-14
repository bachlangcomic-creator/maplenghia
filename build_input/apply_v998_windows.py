from pathlib import Path

p=Path('build_input/apply_v998.py')
s=p.read_text(encoding='utf-8')
s=s.replace(
    'maple.write_text(text, encoding="utf-8")',
    'maple.write_text(text, encoding="utf-8", newline="\\n")',
)
s=s.replace(
    'ui.write_text(u, encoding="utf-8")',
    'ui.write_text(u, encoding="utf-8", newline="\\n")',
)
assert 'newline="\\n"' in s
exec(compile(s, str(p), 'exec'), {'__name__':'__main__'})
