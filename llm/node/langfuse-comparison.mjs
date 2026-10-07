// Model comparison with Langfuse experiments (Node). One run per model, same data.
// Requires ANTHROPIC_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
// (and LANGFUSE_BASE_URL for non-default regions or self-hosting).
import Anthropic from "@anthropic-ai/sdk";
import { LangfuseClient } from "@langfuse/client";
import { LangfuseSpanProcessor } from "@langfuse/otel";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { SYSTEM, runComparison } from "./comparison.mjs";

const otel = new NodeSDK({ spanProcessors: [new LangfuseSpanProcessor()] });
otel.start();

const anthropic = new Anthropic();
const langfuse = new LangfuseClient();

async function callModel(model, question) {
  const response = await anthropic.messages.create({
    model,
    max_tokens: 64,
    system: SYSTEM,
    messages: [{ role: "user", content: question }],
  });
  return response.content[0].text;
}

try {
  const means = await runComparison({ langfuse, callModel });
  for (const [model, mean] of Object.entries(means)) console.log(`${model}: ${mean.toFixed(2)}`);
} finally {
  await langfuse.flush();
  await otel.shutdown();
}
