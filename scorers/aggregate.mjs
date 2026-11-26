// Aggregation: per-model stats, per-task breakdown, pairwise comparison,
// difficulty weighting, and reliability metrics.
// Warm-up runs are excluded from scoring. infra_error/timeout runs are
// excluded from correctness stats but reported separately.

function mean(xs) { return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null; }
function stddev(xs) {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  return Math.sqrt(xs.reduce((a, x) => a + (x - m) ** 2, 0) / (xs.length - 1));
}

export function aggregate(records) {
  const byModel = {};
  for (const r of records) {
    const id = r.manifest.model_id;
    byModel[id] ??= { model: id, family: r.manifest.model_family, quant: r.manifest.quant, hardware: r.manifest.hardware ?? null, scored: [], infra_errors: 0, timeouts: 0 };
    const b = byModel[id];
    if (r.status === "infra_error") { b.infra_errors++; continue; }
    if (r.status === "timeout") { b.timeouts++; continue; }
    if (r.warmup) continue;
    b.scored.push(r);
  }

  // Per-task breakdown per model
  function taskBreakdown(scored) {
    const tasks = {};
    for (const r of scored) {
      const t = r.manifest.task_id;
      tasks[t] ??= { pass: 0, total: 0, secs: [], tokens_in: [], tokens_out: [], partial_scores: [] };
      const entry = tasks[t];
      entry.total++;
      if (r.ok) entry.pass++;
      if (r.metrics?.secs != null) entry.secs.push(r.metrics.secs);
      if (r.metrics?.uIn != null) entry.tokens_in.push(r.metrics.uIn);
      if (r.metrics?.uOut != null) entry.tokens_out.push(r.metrics.uOut);
      if (r.oracle?.partial_credit != null) entry.partial_scores.push(r.oracle.partial_credit);
    }
    return Object.fromEntries(Object.entries(tasks).map(([id, v]) => [id, {
      pass_rate: v.pass / v.total,
      trials: v.total,
      passed: v.pass,
      mean_secs: mean(v.secs),
      mean_tokens_in: mean(v.tokens_in),
      mean_tokens_out: mean(v.tokens_out),
      mean_partial_credit: v.partial_scores.length ? mean(v.partial_scores) : null,
    }]));
  }

  const models = Object.values(byModel).map((b) => {
    const execs = b.scored.filter((r) => r.execution);
    const totalSecs = b.scored.reduce((a, r) => a + (r.metrics?.secs ?? 0), 0);
    const totalTokens = b.scored.reduce((a, r) => a + (r.metrics?.uIn ?? 0) + (r.metrics?.uOut ?? 0), 0);
    // Recovery: trials where the model had tool errors but still passed
    const recovered = b.scored.filter((r) => (r.metrics?.toolErrors ?? 0) > 0 && r.ok).length;
    const hadErrors = b.scored.filter((r) => (r.metrics?.toolErrors ?? 0) > 0).length;

    return {
      model: b.model,
      family: b.family,
      quant: b.quant,
      hardware: b.hardware,
      scored_trials: b.scored.length,
      pass_rate: b.scored.length ? b.scored.filter((r) => r.ok).length / b.scored.length : null,
      // Partial credit (from hidden test SCORE lines)
      mean_partial_credit: mean(b.scored.map((r) => r.oracle?.partial_credit).filter((x) => x != null)) || null,
      plan_to_code_rate: execs.length ? execs.filter((r) => r.execution.ok).length / execs.length : null,
      // Time and throughput
      mean_secs: mean(b.scored.map((r) => r.metrics?.secs ?? 0)),
      secs_stddev: stddev(b.scored.map((r) => r.metrics?.secs ?? 0)),
      tokens_per_sec: totalSecs > 0 ? totalTokens / totalSecs : null,
      mean_turns: mean(b.scored.map((r) => r.metrics?.turns ?? 0)),
      mean_tokens_in: mean(b.scored.map((r) => r.metrics?.uIn ?? 0)),
      mean_tokens_out: mean(b.scored.map((r) => r.metrics?.uOut ?? 0)),
      // Reliability
      infra_errors: b.infra_errors,
      timeouts: b.timeouts,
      recovery_rate: hadErrors > 0 ? recovered / hadErrors : null,
      error_trials: hadErrors,
      // Per-task breakdown
      tasks: taskBreakdown(b.scored),
    };
  });

  // Pairwise win rate on common (task, repeat) pairs where both models scored.
  const pairs = [];
  const modelIds = Object.keys(byModel);
  for (let i = 0; i < modelIds.length; i++) {
    for (let j = i + 1; j < modelIds.length; j++) {
      const [A, B] = [modelIds[i], modelIds[j]];
      let aWins = 0, bWins = 0, ties = 0;
      const taskIds = new Set([...byModel[A].scored, ...byModel[B].scored].map((r) => r.manifest.task_id));
      for (const t of taskIds) {
        const ap = byModel[A].scored.filter((r) => r.manifest.task_id === t && r.ok).length;
        const bp = byModel[B].scored.filter((r) => r.manifest.task_id === t && r.ok).length;
        if (ap > bp) aWins++; else if (bp > ap) bWins++; else ties++;
      }
      pairs.push({ model_a: A, model_b: B, a_wins: aWins, b_wins: bWins, ties });
    }
  }

  // Difficulty weighting: tasks where all models agree (all pass or all fail)
  // have low discriminative power. Weight = 1 - |mean_pass_rate - 0.5| * 2
  // (1.0 = perfectly discriminative at 50%, 0.0 = no signal)
  const allTaskIds = new Set(records.filter((r) => !r.warmup).map((r) => r.manifest.task_id));
  const task_weights = {};
  for (const t of allTaskIds) {
    const passRates = modelIds.map((id) => {
      const scored = byModel[id].scored.filter((r) => r.manifest.task_id === t);
      return scored.length ? scored.filter((r) => r.ok).length / scored.length : null;
    }).filter((x) => x != null);
    if (passRates.length < 2) { task_weights[t] = 1.0; continue; } // can't judge with one model
    const avgRate = passRates.reduce((a, b) => a + b, 0) / passRates.length;
    task_weights[t] = Math.max(0, 1 - Math.abs(avgRate - 0.5) * 2);
  }

  // Weighted pass rate per model (using task discriminative power)
  for (const m of models) {
    const weighted = Object.entries(m.tasks).map(([t, v]) => ({
      weight: task_weights[t] ?? 1.0,
      rate: v.pass_rate,
    }));
    const totalWeight = weighted.reduce((a, x) => a + x.weight, 0);
    m.weighted_pass_rate = totalWeight > 0
      ? weighted.reduce((a, x) => a + x.rate * x.weight, 0) / totalWeight
      : null;
  }

  // Disputed cases for human review: judge errors, or borderline rubric scores
  const disputed = records
    .filter((r) => !r.warmup && r.manifest.task_id)
    .map((r) => {
      if (r.judge?.error) return { model: r.manifest.model_id, task: r.manifest.task_id, reason: `judge error: ${r.judge.error}` };
      if (r.judge?.weighted_avg != null && r.threshold != null) {
        const diff = Math.abs(r.judge.weighted_avg - r.threshold);
        if (diff <= 0.5) return { model: r.manifest.model_id, task: r.manifest.task_id, reason: `borderline rubric ${r.judge.weighted_avg} vs threshold ${r.threshold}` };
      }
      return null;
    })
    .filter(Boolean);

  return {
    generated_at: new Date().toISOString(),
    models,
    pairwise: pairs,
    task_weights,
    disputed,
  };
}
