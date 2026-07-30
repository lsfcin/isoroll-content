# build.py — assemble painter-feel-rig.html from rig.frag + kit_b64.txt (repo copy; publish via Artifact tool, same URL)
import pathlib
d = pathlib.Path(__file__).parent
frag = (d / "rig.frag").read_text()
kit = (d / "kit_b64.txt").read_text()
keep = [l for l in kit.splitlines() if l.startswith('"floor"') or l.startswith('"wall"')]
out = frag.replace("/*__KIT_SRC__*/", "\n".join(keep))
target = pathlib.Path("/tmp") / "painter-feel-rig.html"
target.write_text(out)
print("built", len(out), "->", target)
