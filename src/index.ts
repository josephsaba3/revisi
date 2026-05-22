import { Container } from "@cloudflare/containers";
import { env } from "cloudflare:workers";

export class BrandVoiceAuditorContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";

  envVars = {
    LLM_PROVIDER: env.LLM_PROVIDER || "openai",
    LLM_ANALYSIS_PROMPT: env.LLM_ANALYSIS_PROMPT,
    OPENAI_API_KEY: env.OPENAI_API_KEY,
    DATABASE_URL: env.DATABASE_URL,
    OPENAI_MODEL: env.OPENAI_MODEL || "gpt-5.1-mini",
    OPENAI_REASONING_EFFORT: env.OPENAI_REASONING_EFFORT || "low",
    ANTHROPIC_API_KEY: env.ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL: env.ANTHROPIC_MODEL || "claude-sonnet-4-6",
    ANTHROPIC_MAX_TOKENS: env.ANTHROPIC_MAX_TOKENS || "12000",
    PUBLIC_SITE_URL: env.PUBLIC_SITE_URL
  };
}

export interface Env {
  BRAND_VOICE_AUDITOR: DurableObjectNamespace<BrandVoiceAuditorContainer>;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/healthz") {
      return new Response("ok", { status: 200 });
    }

    const container = env.BRAND_VOICE_AUDITOR.getByName("web");
    return container.fetch(request);
  }
};
