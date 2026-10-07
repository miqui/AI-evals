// Pure pieces shared by the Langfuse run and its offline test.
export const MODELS = [
  "claude-haiku-4-5-20251001",
  "claude-sonnet-5-5",
  "claude-opus-5-5",
];

export const SYSTEM = "Answer with only the answer, no explanation.";

export const DATA = [
  { input: "What is the capital of France?", expectedOutput: "Paris" },
  {
    input: "Which movie features a detective hunting a killer using the seven deadly sins?",
    expectedOutput: "Se7en",
  },
  { input: "What is 17 * 3?", expectedOutput: "51" },
  { input: "What is the chemical symbol for gold?", expectedOutput: "Au" },
  { input: "Who wrote the novel '1984'?", expectedOutput: "Orwell" },
];

// Deterministic scorer: case-insensitive substring match.
export function includesExpected({ output, expectedOutput }) {
  const hit = String(output ?? "").toLowerCase().includes(String(expectedOutput).toLowerCase());
  return { name: "includes", value: hit ? 1 : 0 };
}

// Run one experiment per model; returns mean `includes` score per model.
export async function runComparison({ langfuse, callModel, models = MODELS, data = DATA }) {
  const means = {};
  for (const model of models) {
    const result = await langfuse.experiment.run({
      name: "Model comparison",
      runName: `model-comparison / ${model}`,
      description: `Same ${data.length} questions, model=${model}`,
      metadata: { model },
      data,
      task: async (item) => callModel(model, item.input),
      evaluators: [async (params) => includesExpected(params)],
    });
    const scores = result.itemResults
      .flatMap((r) => r.evaluations)
      .filter((e) => e.name === "includes")
      .map((e) => e.value);
    means[model] = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
  }
  return means;
}
