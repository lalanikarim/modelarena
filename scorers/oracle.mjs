// Oracle scorer: runs hidden tests against a trial's workdir. Tests are plain
// Python scripts (exit 0 = pass). They live in the task fixture dir and are
// never referenced in prompts, so models cannot see or game them.
//
// Partial credit: if a test prints "SCORE: N/M" on its last stdout line,
// the oracle records that as partial credit even when the exit code is non-zero.
import { execFileSync } from "node:child_process";
import { join } from "node:path";

/**
 * Run hidden tests for a task against workdir.
 * @param {string} [testRelPaths] override the test list (e.g. bonus tests)
 * @returns {{ pass: boolean, partial_credit: number|null, details: Array<{test: string, ok: boolean, output: string, score?: {passed: number, total: number}}> }}
 */
export function runOracle(task, workdir, testRelPaths) {
  const details = [];
  let pass = true;
  let totalPassed = 0, totalAssertions = 0;

  for (const rel of testRelPaths ?? task.oracle.hidden_tests ?? []) {
    const testPath = join(task.dir, rel);
    let ok = false, output = "", score = null;
    try {
      const out = execFileSync("python3", [testPath], { cwd: workdir, timeout: 60000, encoding: "utf8" });
      ok = true;
      output = out.trim().slice(-2000);
      score = parseScore(output);
    } catch (err) {
      const stdout = err.stdout ?? "";
      const stderr = err.stderr ?? "";
      output = (stdout + "\n" + stderr + "\n" + err.message).trim().slice(-2000);
      // Check for SCORE line even on failure (partial credit)
      score = parseScore(stdout);
    }
    if (score) {
      totalPassed += score.passed;
      totalAssertions += score.total;
    }
    details.push({ test: rel, ok, output, ...(score ? { score } : {}) });
    if (!ok) pass = false;
  }

  const partial_credit = totalAssertions > 0 ? totalPassed / totalAssertions : null;
  return { pass, partial_credit, details };
}

/**
 * Parse "SCORE: N/M" from test output. Returns {passed, total} or null.
 */
function parseScore(output) {
  // Look for the last occurrence of SCORE: N/M
  const matches = [...output.matchAll(/SCORE:\s*(\d+)\s*\/\s*(\d+)/g)];
  if (matches.length === 0) return null;
  const last = matches[matches.length - 1];
  const passed = parseInt(last[1], 10);
  const total = parseInt(last[2], 10);
  if (total <= 0 || passed < 0 || passed > total) return null;
  return { passed, total };
}
