"""Test helper: evaluate Pit House binding JavaScript with Node.

Each case is (expression, input) where input is a JS literal string ("NaN", "null",
"'Ryan'", "-0.2"). The input is exposed both as `_result` (for formatters) and as the
value of every `Telemetry.get(...)` call (for visibility conditions).
"""
import json
import shutil
import subprocess

NODE = shutil.which("node")

_RUNNER = """
const cases = %s;
const out = cases.map(([expr, input]) => {
  const v = eval('(' + input + ')');
  const Telemetry = { get: () => ({ value: v }) };
  const r = new Function('_result', 'Telemetry', 'return (' + expr + ');')(v, Telemetry);
  return r === undefined ? null : r;
});
process.stdout.write(JSON.stringify(out));
"""


def run(cases):
    """Evaluate all cases in one Node process; returns the list of results."""
    if NODE is None:
        raise RuntimeError("node not found on PATH")
    script = _RUNNER % json.dumps([list(c) for c in cases])
    done = subprocess.run([NODE, "-e", script], capture_output=True, text=True, check=True)
    return json.loads(done.stdout)
