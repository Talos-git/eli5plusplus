export type ExplainRequest = {
  topic: string;
  complexity: number;
  mandarin: boolean;
};

export type StreamHandler = (chunk: string) => void;

const decodeChunk = (value: Uint8Array, decoder: TextDecoder) => decoder.decode(value, { stream: true });

const extractContentFromLine = (line: string): string => {
  if (!line.startsWith('data:')) {
    return '';
  }
  const payload = line.replace(/^data:\s*/, '').trim();
  if (!payload || payload === '[DONE]') {
    return '';
  }
  try {
    const parsed = JSON.parse(payload);
    const delta = parsed.choices?.[0]?.delta?.content;
    return typeof delta === 'string' ? delta : '';
  } catch {
    return '';
  }
};

export const streamExplanation = async (
  endpoint: string,
  request: ExplainRequest,
  onChunk: StreamHandler,
): Promise<void> => {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok || !response.body) {
    const text = await response.text();
    throw new Error(text || 'Failed to generate explanation.');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffered = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffered += decodeChunk(value, decoder);
    const lines = buffered.split('\n');
    buffered = lines.pop() ?? '';

    for (const line of lines) {
      const content = extractContentFromLine(line);
      if (content) {
        onChunk(content);
      }
    }
  }
};
