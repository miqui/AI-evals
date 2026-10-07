// Offline tests (node --test): no keys, no network.
import assert from "node:assert/strict";
import { test } from "node:test";
import { DATA, includesExpected, runComparison } from "./comparison.mjs";

test("includesExpected is case-insensitive substring match", () => {
  assert.equal(includesExpected({ output: "It is Paris.", expectedOutput: "paris" }).value, 1);
  assert.equal(includesExpected({ output: "Rome", expectedOutput: "Paris" }).value, 0);
});

test("runComparison scores each model with a fake client", async () => {
  const answers = Object.fromEntries(DATA.map((d) => [d.input, d.expectedOutput]));
  // Stand-in for LangfuseClient: runs task + evaluators locally.
  const langfuse = {
    experiment: {
      async run({ data, task, evaluators }) {
        const itemResults = [];
        for (const item of data) {
          const output = await task(item);
          const evaluations = [];
          for (const ev of evaluators) {
            evaluations.push(await ev({ input: item.input, output, expectedOutput: item.expectedOutput }));
          }
          itemResults.push({ evaluations });
        }
        return { itemResults };
      },
    },
  };
  const callModel = async (model, q) => (model === "good" ? answers[q] : "no idea");
  const means = await runComparison({ langfuse, callModel, models: ["good", "bad"] });
  assert.deepEqual(means, { good: 1, bad: 0 });
});
