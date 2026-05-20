import { Container } from "@cloudflare/containers";
import { env } from "cloudflare:workers";

export class BrandVoiceAuditorContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";

  envVars = {
    OPENAI_API_KEY: env.OPENAI_API_KEY,
    DATABASE_URL: env.DATABASE_URL,
    OPENAI_MODEL: env.OPENAI_MODEL || "gpt-5.1-mini",
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
