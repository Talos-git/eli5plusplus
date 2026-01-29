const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

type ExplainRequest = {
  topic: string;
  complexity: number;
  mandarin: boolean;
};

const buildPrompt = ({ topic, complexity, mandarin }: ExplainRequest): string => {
  if (mandarin) {
    return `用中文解释主题 '${topic}'，复杂度水平对应于滑块值 ${complexity}，范围从 0 到 100。在这个范围内，0 意味着 '像我 5 岁一样解释'，50 意味着 '像高中生一样解释'，100 意味着 '像该领域的专家一样解释'。在需要时以结构化的方式提供答案，包括标题和要点。`;
  }

  return `Explain the topic '${topic}' at a complexity level corresponding to a slider value of ${complexity} on a scale of 0 to 100. On this scale, 0 means 'Explain like I'm 5', 50 means 'Explain like I'm a high school student', and 100 means 'Explain like I'm an expert in the field'. Provide the answer in a structured manner with header and bullet points when needed.`;
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405, headers: corsHeaders });
  }

  const apiKey = Deno.env.get('OPENROUTER_API_KEY');
  if (!apiKey) {
    return new Response('OPENROUTER_API_KEY is not configured', { status: 500, headers: corsHeaders });
  }

  const model = Deno.env.get('OPENROUTER_MODEL') ?? 'openai/gpt-4o-mini';

  let payload: ExplainRequest;
  try {
    payload = await req.json();
  } catch {
    return new Response('Invalid JSON payload', { status: 400, headers: corsHeaders });
  }

  if (!payload?.topic || typeof payload.topic !== 'string') {
    return new Response('Topic is required', { status: 400, headers: corsHeaders });
  }

  const prompt = buildPrompt({
    topic: payload.topic,
    complexity: Number.isFinite(payload.complexity) ? payload.complexity : 0,
    mandarin: Boolean(payload.mandarin),
  });

  const openrouterResponse = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      stream: true,
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
    }),
  });

  if (!openrouterResponse.ok) {
    const errorText = await openrouterResponse.text();
    return new Response(errorText, { status: openrouterResponse.status, headers: corsHeaders });
  }

  const headers = new Headers(corsHeaders);
  headers.set('Content-Type', 'text/event-stream');

  return new Response(openrouterResponse.body, {
    status: 200,
    headers,
  });
});
